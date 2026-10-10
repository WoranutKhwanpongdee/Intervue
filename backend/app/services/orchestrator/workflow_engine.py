import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import InterviewSession, QuestionTurn
from app.schemas.interview import CreateInterviewRequest
from app.schemas.llm import AnswerEvaluation, FinalInterviewReport, InterviewQuestion
from app.services.llm.factory import get_llm_provider
from app.services.llm.base import BaseLLMProvider
from app.services.llm.mock import MockLLMProvider
from app.services.orchestrator.state_machine import (
    InterviewStateMachine,
    InterviewState,
    TransitionTrigger,
    NextActionDecision,
    WorkflowContext,
)
from app.services.orchestrator.retry_handler import AsyncRetryHandler, RetryPolicy
from app.services.qc.qc_pipeline import QuestionQualityControlPipeline
from app.services.qc.skill_coverage_tracker import SkillCoverageTracker

logger = logging.getLogger("intervue.orchestrator.engine")


class InterviewWorkflowOrchestrator:
    """
    Core orchestrator controlling the end-to-end interview lifecycle:
    Resume Analysis ➔ Topic Selection ➔ Question Generation ➔ Answer Evaluation ➔ Decision Routing ➔ Report Debrief.
    """

    def __init__(
        self,
        db: AsyncSession,
        provider: Optional[BaseLLMProvider] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        self.db = db
        self.provider = provider or get_llm_provider()
        self.retry_handler = AsyncRetryHandler(retry_policy or RetryPolicy())

    def _build_state_machine(self, session: InterviewSession) -> InterviewStateMachine:
        raw_state = session.current_state or "INITIALIZING"
        try:
            state_enum = InterviewState(raw_state)
        except ValueError:
            state_enum = InterviewState.INITIALIZING

        raw_ctx = session.workflow_context or {}
        ctx = WorkflowContext.model_validate(raw_ctx) if raw_ctx else WorkflowContext(
            session_id=session.id,
            role_title=session.role_title,
            experience_level=session.experience_level,
            interview_type=session.interview_type,
            difficulty=session.difficulty,
            num_questions=session.num_questions,
            current_round_stage=session.current_round_stage,
        )
        return InterviewStateMachine(initial_state=state_enum, context=ctx)

    def _sync_session_state(self, session: InterviewSession, sm: InterviewStateMachine):
        session.current_state = sm.current_state.value
        session.current_round_stage = sm.context.current_round_stage
        session.workflow_context = sm.context.model_dump(mode="json")
        if sm.current_state == InterviewState.COMPLETED:
            session.status = "completed"
        elif session.status != "abandoned":
            session.status = "in_progress"

    # -------------------------------------------------------------------------
    # 1. Initialize & Start Interview Session
    # -------------------------------------------------------------------------
    async def initialize_and_start(self, req: CreateInterviewRequest) -> InterviewSession:
        """
        Executes:
        INITIALIZING ➔ RESUME_ANALYSIS ➔ TOPIC_SELECTION ➔ QUESTION_GENERATION ➔ AWAITING_ANSWER
        """
        session = InterviewSession(
            role_title=req.role_title,
            experience_level=req.experience_level,
            interview_type=req.interview_type,
            difficulty=req.difficulty,
            num_questions=req.num_questions,
            resume_text=req.resume_text,
            job_description=req.job_description,
            status="in_progress",
            current_state=InterviewState.INITIALIZING.value
        )
        self.db.add(session)
        await self.db.flush()

        sm = self._build_state_machine(session)

        # Step 1: Resume Analysis
        sm.transition_to(
            InterviewState.RESUME_ANALYSIS,
            trigger=TransitionTrigger.ANALYZE_PROFILE,
            details="Extracting candidate profile, key stack, and grounding anchors from resume."
        )
        if req.resume_text:
            sm.context.extracted_skills = ["Analyzed Resume Context"]

        # Step 2: Topic Selection
        sm.transition_to(
            InterviewState.TOPIC_SELECTION,
            trigger=TransitionTrigger.SELECT_TOPIC,
            details=f"Calibrating initial round stage for {req.interview_type} track."
        )
        if req.interview_type == "Full-Loop":
            sm.context.current_round_stage = "Round 1: HR & Culture Fit"
            sm.context.current_persona = "Senior Talent Partner"
        else:
            sm.context.current_round_stage = f"{req.interview_type} Track"
            sm.context.current_persona = "Lead Interviewer"

        # Step 3: Question Generation (with retry & fallback)
        sm.transition_to(
            InterviewState.QUESTION_GENERATION,
            trigger=TransitionTrigger.GENERATE_QUESTION,
            details="Generating initial grounded interview question."
        )

        async def generate_q():
            return await self.provider.generate_initial_question(
                role_title=req.role_title,
                experience_level=req.experience_level,
                interview_type=req.interview_type,
                difficulty=req.difficulty,
                resume_text=req.resume_text,
                job_description=req.job_description
            )

        async def fallback_q():
            mock = MockLLMProvider()
            return await mock.generate_initial_question(
                role_title=req.role_title,
                experience_level=req.experience_level,
                interview_type=req.interview_type,
                difficulty=req.difficulty,
                resume_text=req.resume_text,
                job_description=req.job_description
            )

        initial_q: InterviewQuestion = await self.retry_handler.execute_with_retry(
            operation_name="generate_initial_question",
            coro_func=generate_q,
            fallback_func=fallback_q
        )

        # Apply Question Quality Control (QC) & Validation
        target_skills = SkillCoverageTracker.extract_target_skills(req.resume_text, req.job_description)
        initial_q, qc_audit = QuestionQualityControlPipeline.audit_and_refine(
            question=initial_q,
            previous_questions=[],
            target_skills=target_skills,
            accumulated_skills=[],
            base_difficulty=req.difficulty,
            experience_level=req.experience_level
        )

        # Step 4: Record First Turn & Await Answer
        first_turn = QuestionTurn(
            session_id=session.id,
            turn_number=1,
            is_followup=False,
            question_text=initial_q.question,
            question_category=initial_q.category,
            difficulty=initial_q.difficulty,
            expected_points=initial_q.expected_concepts,
            resume_context_used=initial_q.resume_context_used,
            adaptive_context=initial_q.adaptive_context,
            round_stage=initial_q.round_stage or sm.context.current_round_stage,
            interviewer_persona=initial_q.interviewer_persona or sm.context.current_persona,
            qc_quality_score=qc_audit.overall_quality_score,
            qc_clarity_score=qc_audit.clarity_score,
            skills_covered=qc_audit.target_skills_covered,
            qc_audit_passed=qc_audit.is_valid
        )
        self.db.add(first_turn)

        sm.context.active_topic = initial_q.category
        sm.context.covered_topics.extend(qc_audit.target_skills_covered or [initial_q.category])
        sm.transition_to(
            InterviewState.AWAITING_ANSWER,
            trigger=TransitionTrigger.AWAIT_INPUT,
            details="Question ready and QC verified. Waiting for candidate submission."
        )

        self._sync_session_state(session, sm)
        await self.db.commit()

        # Eager load with turns
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session.id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()

    # -------------------------------------------------------------------------
    # 2. Submit Answer, Evaluate & Orchestrate Next Action
    # -------------------------------------------------------------------------
    async def submit_and_evaluate(
        self,
        session_id: str,
        turn_id: str,
        answer: str
    ) -> Tuple[AnswerEvaluation, QuestionTurn, Optional[QuestionTurn], bool]:
        """
        Executes:
        AWAITING_ANSWER ➔ EVALUATING_ANSWER ➔ DECIDING_NEXT_ACTION ➔
          (Branch A) DEEP_DIVE_PROBE ➔ AWAITING_ANSWER
          (Branch B) TOPIC_SELECTION ➔ QUESTION_GENERATION ➔ AWAITING_ANSWER
          (Branch C) COMPILING_REPORT ➔ COMPLETED
        """
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        current_turn = next((t for t in session.turns if t.id == turn_id), None)
        if not current_turn:
            raise ValueError(f"Turn {turn_id} not found in session")

        sm = self._build_state_machine(session)

        # Transition to EVALUATING_ANSWER
        if sm.current_state != InterviewState.AWAITING_ANSWER:
            sm.current_state = InterviewState.AWAITING_ANSWER

        sm.transition_to(
            InterviewState.EVALUATING_ANSWER,
            trigger=TransitionTrigger.SUBMIT_ANSWER,
            details=f"Evaluating turn {current_turn.turn_number} answer against multi-metric rubric."
        )

        async def evaluate_op():
            return await self.provider.evaluate_answer(
                role_title=session.role_title,
                experience_level=session.experience_level,
                interview_type=session.interview_type,
                question_text=current_turn.question_text,
                expected_concepts=current_turn.expected_points or [],
                user_answer=answer,
                is_followup=current_turn.is_followup,
                turn_number=current_turn.turn_number,
                total_questions=session.num_questions
            )

        async def evaluate_fallback():
            mock = MockLLMProvider()
            return await mock.evaluate_answer(
                role_title=session.role_title,
                experience_level=session.experience_level,
                interview_type=session.interview_type,
                question_text=current_turn.question_text,
                expected_concepts=current_turn.expected_points or [],
                user_answer=answer,
                is_followup=current_turn.is_followup,
                turn_number=current_turn.turn_number,
                total_questions=session.num_questions
            )

        evaluation: AnswerEvaluation = await self.retry_handler.execute_with_retry(
            operation_name="evaluate_answer",
            coro_func=evaluate_op,
            fallback_func=evaluate_fallback
        )

        # Persist evaluation on turn
        current_turn.user_answer = answer
        current_turn.answered_at = datetime.utcnow()
        current_turn.technical_score = evaluation.technical_score
        current_turn.relevance_score = evaluation.relevance_score
        current_turn.clarity_score = evaluation.clarity_score
        current_turn.completeness_score = evaluation.completeness_score
        current_turn.turn_score = evaluation.turn_score
        current_turn.feedback = evaluation.feedback
        current_turn.key_positives = evaluation.key_positives
        current_turn.areas_for_improvement = evaluation.areas_for_improvement
        current_turn.sample_ideal_answer = evaluation.sample_ideal_answer
        current_turn.latent_blindspot = evaluation.latent_blindspot
        current_turn.bluff_detected = evaluation.bluff_detected
        current_turn.buzzwords_detected = evaluation.buzzwords_detected
        current_turn.probing_rationale = evaluation.probing_rationale

        # Transition to DECIDING_NEXT_ACTION
        sm.transition_to(
            InterviewState.DECIDING_NEXT_ACTION,
            trigger=TransitionTrigger.DECIDE_NEXT,
            details="Determining next step based on bluff detection, performance, and turn counts."
        )

        core_answered_count = len([t for t in session.turns if not t.is_followup and (t.user_answer is not None or t.id == turn_id)])
        total_core_needed = session.num_questions
        next_turn: Optional[QuestionTurn] = None
        is_completed = False

        should_followup = (evaluation.requires_followup or evaluation.bluff_detected) and not current_turn.is_followup and core_answered_count <= total_core_needed

        if should_followup:
            # Branch A: DEEP_DIVE_PROBE
            sm.transition_to(
                InterviewState.DEEP_DIVE_PROBE,
                trigger=TransitionTrigger.TRIGGER_FOLLOWUP,
                details=f"Triggering deep-dive probe. Bluff flagged: {evaluation.bluff_detected}."
            )

            async def gen_followup():
                return await self.provider.generate_followup_question(
                    role_title=session.role_title,
                    experience_level=session.experience_level,
                    parent_question=current_turn.question_text,
                    user_answer=answer,
                    evaluation=evaluation,
                    difficulty=session.difficulty
                )

            async def fallback_followup():
                mock = MockLLMProvider()
                return await mock.generate_followup_question(
                    role_title=session.role_title,
                    experience_level=session.experience_level,
                    parent_question=current_turn.question_text,
                    user_answer=answer,
                    evaluation=evaluation,
                    difficulty=session.difficulty
                )

            followup_q = await self.retry_handler.execute_with_retry(
                operation_name="generate_followup_question",
                coro_func=gen_followup,
                fallback_func=fallback_followup
            )

            # Apply Question Quality Control (QC) & Validation to follow-up probe
            target_skills = SkillCoverageTracker.extract_target_skills(session.resume_text, session.job_description)
            prev_questions = [t.question_text for t in session.turns]
            past_scores = [t.turn_score for t in session.turns if t.turn_score is not None]
            
            followup_q, qc_audit = QuestionQualityControlPipeline.audit_and_refine(
                question=followup_q,
                previous_questions=prev_questions,
                target_skills=target_skills,
                accumulated_skills=sm.context.covered_topics,
                base_difficulty=session.difficulty,
                experience_level=session.experience_level,
                turn_scores=past_scores
            )

            probe_note = (
                f"🔍 Depth Probe ({', '.join(evaluation.buzzwords_detected)}): {evaluation.probing_rationale}"
                if evaluation.bluff_detected and evaluation.buzzwords_detected
                else (evaluation.followup_reason or "Drilling deeper into trade-offs")
            )

            next_turn = QuestionTurn(
                session_id=session.id,
                turn_number=len(session.turns) + 1,
                is_followup=True,
                parent_turn_id=current_turn.id,
                question_text=followup_q.question,
                question_category=followup_q.category,
                difficulty=followup_q.difficulty,
                expected_points=followup_q.expected_concepts,
                resume_context_used=followup_q.resume_context_used,
                adaptive_context=followup_q.adaptive_context or probe_note,
                round_stage=followup_q.round_stage or current_turn.round_stage,
                interviewer_persona=followup_q.interviewer_persona or current_turn.interviewer_persona,
                qc_quality_score=qc_audit.overall_quality_score,
                qc_clarity_score=qc_audit.clarity_score,
                skills_covered=qc_audit.target_skills_covered,
                qc_audit_passed=qc_audit.is_valid
            )
            self.db.add(next_turn)
            sm.context.covered_topics.extend(qc_audit.target_skills_covered)

            sm.transition_to(
                InterviewState.AWAITING_ANSWER,
                trigger=TransitionTrigger.AWAIT_INPUT,
                details="Follow-up depth probe ready for candidate."
            )

        elif core_answered_count < total_core_needed:
            # Branch B: TOPIC_SELECTION ➔ QUESTION_GENERATION
            sm.transition_to(
                InterviewState.TOPIC_SELECTION,
                trigger=TransitionTrigger.ADVANCE_TOPIC,
                details=f"Advancing to core question turn {core_answered_count + 1}."
            )

            sm.transition_to(
                InterviewState.QUESTION_GENERATION,
                trigger=TransitionTrigger.GENERATE_QUESTION,
                details="Generating next adaptive question with full multi-turn memory."
            )

            previous_turns_data = [
                {
                    "turn_number": t.turn_number,
                    "question_text": t.question_text,
                    "category": t.question_category,
                    "difficulty": t.difficulty,
                    "user_answer": t.user_answer,
                    "turn_score": t.turn_score,
                    "technical_score": t.technical_score,
                    "relevance_score": t.relevance_score,
                    "clarity_score": t.clarity_score,
                    "completeness_score": t.completeness_score,
                    "feedback": t.feedback,
                    "key_positives": t.key_positives or [],
                    "areas_for_improvement": t.areas_for_improvement or []
                }
                for t in session.turns
                if t.user_answer is not None or t.id == turn_id
            ]

            async def gen_next_q():
                return await self.provider.generate_next_question(
                    role_title=session.role_title,
                    experience_level=session.experience_level,
                    interview_type=session.interview_type,
                    difficulty=session.difficulty,
                    turn_number=core_answered_count + 1,
                    total_questions=total_core_needed,
                    previous_turns=previous_turns_data,
                    resume_text=session.resume_text,
                    job_description=session.job_description
                )

            async def fallback_next_q():
                mock = MockLLMProvider()
                return await mock.generate_next_question(
                    role_title=session.role_title,
                    experience_level=session.experience_level,
                    interview_type=session.interview_type,
                    difficulty=session.difficulty,
                    turn_number=core_answered_count + 1,
                    total_questions=total_core_needed,
                    previous_turns=previous_turns_data,
                    resume_text=session.resume_text,
                    job_description=session.job_description
                )

            next_q = await self.retry_handler.execute_with_retry(
                operation_name="generate_next_question",
                coro_func=gen_next_q,
                fallback_func=fallback_next_q
            )

            # Apply Question Quality Control (QC) & Validation to next question
            target_skills = SkillCoverageTracker.extract_target_skills(session.resume_text, session.job_description)
            prev_questions = [t.question_text for t in session.turns]
            past_scores = [t.turn_score for t in session.turns if t.turn_score is not None]

            next_q, qc_audit = QuestionQualityControlPipeline.audit_and_refine(
                question=next_q,
                previous_questions=prev_questions,
                target_skills=target_skills,
                accumulated_skills=sm.context.covered_topics,
                base_difficulty=session.difficulty,
                experience_level=session.experience_level,
                turn_scores=past_scores
            )

            next_turn = QuestionTurn(
                session_id=session.id,
                turn_number=len(session.turns) + 1,
                is_followup=False,
                question_text=next_q.question,
                question_category=next_q.category,
                difficulty=next_q.difficulty,
                expected_points=next_q.expected_concepts,
                resume_context_used=next_q.resume_context_used,
                adaptive_context=next_q.adaptive_context,
                round_stage=next_q.round_stage,
                interviewer_persona=next_q.interviewer_persona,
                qc_quality_score=qc_audit.overall_quality_score,
                qc_clarity_score=qc_audit.clarity_score,
                skills_covered=qc_audit.target_skills_covered,
                qc_audit_passed=qc_audit.is_valid
            )
            self.db.add(next_turn)

            sm.context.active_topic = next_q.category
            sm.context.covered_topics.extend(qc_audit.target_skills_covered or [next_q.category])
            sm.context.current_round_stage = next_q.round_stage
            sm.context.current_persona = next_q.interviewer_persona

            sm.transition_to(
                InterviewState.AWAITING_ANSWER,
                trigger=TransitionTrigger.AWAIT_INPUT,
                details="Next core question presented. Awaiting answer."
            )

        else:
            # Branch C: COMPILING_REPORT ➔ COMPLETED
            is_completed = True
            sm.transition_to(
                InterviewState.COMPILING_REPORT,
                trigger=TransitionTrigger.COMPILE_REPORT,
                details="Session finished. Compiling synthesized report debrief."
            )
            await self._compile_and_complete_report(session, sm)

        self._sync_session_state(session, sm)
        await self.db.commit()

        if next_turn:
            await self.db.refresh(next_turn)
        await self.db.refresh(current_turn)

        return evaluation, current_turn, next_turn, is_completed

    # -------------------------------------------------------------------------
    # 3. Compile Report & Finalize
    # -------------------------------------------------------------------------
    async def _compile_and_complete_report(
        self,
        session: InterviewSession,
        sm: InterviewStateMachine
    ) -> FinalInterviewReport:
        turns_data = [
            {
                "question_text": t.question_text,
                "is_followup": t.is_followup,
                "user_answer": t.user_answer,
                "technical_score": t.technical_score,
                "relevance_score": t.relevance_score,
                "clarity_score": t.clarity_score,
                "completeness_score": t.completeness_score,
                "turn_score": t.turn_score,
                "feedback": t.feedback,
            }
            for t in session.turns
            if t.user_answer is not None
        ]

        async def gen_report():
            return await self.provider.generate_final_report(
                role_title=session.role_title,
                experience_level=session.experience_level,
                interview_type=session.interview_type,
                difficulty=session.difficulty,
                turns=turns_data,
                resume_text=session.resume_text,
                job_description=session.job_description
            )

        async def fallback_report():
            mock = MockLLMProvider()
            return await mock.generate_final_report(
                role_title=session.role_title,
                experience_level=session.experience_level,
                interview_type=session.interview_type,
                difficulty=session.difficulty,
                turns=turns_data,
                resume_text=session.resume_text,
                job_description=session.job_description
            )

        report: FinalInterviewReport = await self.retry_handler.execute_with_retry(
            operation_name="generate_final_report",
            coro_func=gen_report,
            fallback_func=fallback_report
        )

        session.overall_score = report.overall_score
        session.readiness_level = report.readiness_level
        session.summary = report.summary
        session.strengths = report.strengths
        session.weaknesses = report.weaknesses
        session.hidden_weaknesses = [
            hw.model_dump() if hasattr(hw, "model_dump") else hw
            for hw in report.hidden_weaknesses
        ]
        session.skill_map = [
            sm_item.model_dump() if hasattr(sm_item, "model_dump") else sm_item
            for sm_item in report.skill_map
        ]
        session.depth_audit = [
            da.model_dump() if hasattr(da, "model_dump") else da
            for da in report.depth_audit
        ]
        session.round_evaluations = [
            re.model_dump() if hasattr(re, "model_dump") else re
            for re in report.round_evaluations
        ]
        session.hiring_committee_verdict = report.hiring_committee_verdict
        session.recommended_topics = report.recommended_topics
        session.closing_advice = report.closing_advice

        sm.transition_to(
            InterviewState.COMPLETED,
            trigger=TransitionTrigger.COMPLETE,
            details="Final report synthesized and persisted."
        )
        return report

    # -------------------------------------------------------------------------
    # 4. Persistence & Session Resumption
    # -------------------------------------------------------------------------
    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Rehydrates an existing interview session, audits turns integrity,
        and restores the state machine to its ready state.
        """
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        sm = self._build_state_machine(session)

        # Audit unanswered turn
        unanswered_turn = next((t for t in session.turns if t.user_answer is None), None)

        if session.status == "completed" or sm.current_state == InterviewState.COMPLETED:
            return {
                "session": session,
                "current_state": InterviewState.COMPLETED.value,
                "is_completed": True,
                "active_turn": None,
                "message": "Interview session already completed."
            }

        if unanswered_turn:
            sm.current_state = InterviewState.AWAITING_ANSWER
            sm.transition_to(
                InterviewState.AWAITING_ANSWER,
                trigger=TransitionTrigger.RESUME,
                details=f"Resumed session at unanswered turn {unanswered_turn.turn_number}."
            )
            self._sync_session_state(session, sm)
            await self.db.commit()
            return {
                "session": session,
                "current_state": sm.current_state.value,
                "is_completed": False,
                "active_turn": unanswered_turn,
                "message": f"Resumed at turn {unanswered_turn.turn_number}."
            }

        # If all turns were answered but session not finalized, compile report now
        sm.transition_to(
            InterviewState.COMPILING_REPORT,
            trigger=TransitionTrigger.COMPILE_REPORT,
            details="All turns answered. Compiling report on resume."
        )
        await self._compile_and_complete_report(session, sm)
        self._sync_session_state(session, sm)
        await self.db.commit()

        return {
            "session": session,
            "current_state": sm.current_state.value,
            "is_completed": True,
            "active_turn": None,
            "message": "Session completed and final scorecard generated."
        }

    # -------------------------------------------------------------------------
    # 5. Error Recovery
    # -------------------------------------------------------------------------
    async def recover_session(self, session_id: str) -> InterviewSession:
        """
        Rolls back session from FAILED or RECOVERING to last known stable checkpoint.
        """
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        sm = self._build_state_machine(session)
        target_checkpoint = sm.context.last_checkpoint_state or InterviewState.AWAITING_ANSWER

        sm.current_state = InterviewState.RECOVERING
        sm.transition_to(
            target_checkpoint,
            trigger=TransitionTrigger.RECOVER,
            details=f"Recovered session state back to checkpoint: {target_checkpoint.value}."
        )

        self._sync_session_state(session, sm)
        await self.db.commit()
        
        stmt_reload = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res_reload = await self.db.execute(stmt_reload)
        return res_reload.scalar_one()

    # -------------------------------------------------------------------------
    # 6. Conclude Early
    # -------------------------------------------------------------------------
    async def finish_early(self, session_id: str) -> InterviewSession:
        """Force conclude ongoing session and compile report."""
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        sm = self._build_state_machine(session)
        sm.current_state = InterviewState.AWAITING_ANSWER
        sm.transition_to(
            InterviewState.COMPILING_REPORT,
            trigger=TransitionTrigger.COMPILE_REPORT,
            details="Candidate requested early conclusion."
        )

        await self._compile_and_complete_report(session, sm)
        self._sync_session_state(session, sm)
        await self.db.commit()
        
        stmt_reload = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res_reload = await self.db.execute(stmt_reload)
        return res_reload.scalar_one()

