import logging
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import InterviewSession, QuestionTurn
from app.schemas.interview import CreateInterviewRequest
from app.services.llm.factory import get_llm_provider
from app.schemas.llm import AnswerEvaluation, FinalInterviewReport

logger = logging.getLogger("intervue.engine")


class InterviewEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = get_llm_provider()

    async def create_session(self, req: CreateInterviewRequest) -> InterviewSession:
        """Create new interview session and generate the initial question."""
        session = InterviewSession(
            role_title=req.role_title,
            experience_level=req.experience_level,
            interview_type=req.interview_type,
            difficulty=req.difficulty,
            num_questions=req.num_questions,
            resume_text=req.resume_text,
            job_description=req.job_description,
            status="in_progress"
        )
        self.db.add(session)
        await self.db.flush()

        # Generate first question via LLM
        initial_q = await self.provider.generate_initial_question(
            role_title=req.role_title,
            experience_level=req.experience_level,
            interview_type=req.interview_type,
            difficulty=req.difficulty,
            resume_text=req.resume_text,
            job_description=req.job_description
        )

        first_turn = QuestionTurn(
            session_id=session.id,
            turn_number=1,
            is_followup=False,
            question_text=initial_q.question,
            question_category=initial_q.category,
            difficulty=initial_q.difficulty,
            expected_points=initial_q.expected_concepts,
            resume_context_used=initial_q.resume_context_used,
            adaptive_context=initial_q.adaptive_context
        )
        self.db.add(first_turn)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def process_answer(
        self,
        session_id: str,
        turn_id: str,
        answer: str
    ) -> Tuple[AnswerEvaluation, QuestionTurn, Optional[QuestionTurn], bool]:
        """
        Evaluate candidate's answer for the turn.
        Then adaptively decides whether to trigger a deep-dive follow-up or move to the next topic.
        """
        # Fetch session with all turns
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Find targeted turn
        current_turn = next((t for t in session.turns if t.id == turn_id), None)
        if not current_turn:
            raise ValueError(f"Turn {turn_id} not found in session")

        # Evaluate answer via LLM
        evaluation = await self.provider.evaluate_answer(
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

        # Update current turn record
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

        # Count how many core (non-followup) questions have been answered
        core_answered_count = len([t for t in session.turns if not t.is_followup and t.user_answer is not None])
        total_core_needed = session.num_questions

        next_turn: Optional[QuestionTurn] = None
        is_completed = False

        # Adaptive logic:
        # If evaluation suggests follow-up and the current turn wasn't already a follow-up,
        # generate a contextual follow-up question.
        if evaluation.requires_followup and not current_turn.is_followup and core_answered_count <= total_core_needed:
            followup_q = await self.provider.generate_followup_question(
                role_title=session.role_title,
                experience_level=session.experience_level,
                parent_question=current_turn.question_text,
                user_answer=answer,
                evaluation=evaluation,
                difficulty=session.difficulty
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
                adaptive_context=followup_q.adaptive_context or f"Follow-up probe on response to Q{current_turn.turn_number}: {evaluation.followup_reason or 'Drilling deeper into trade-offs'}"
            )
            self.db.add(next_turn)
        elif core_answered_count < total_core_needed:
            # Generate next main question with full memory of previous answers & performance
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
                if t.user_answer is not None
            ]
            next_q = await self.provider.generate_next_question(
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
            next_turn = QuestionTurn(
                session_id=session.id,
                turn_number=len(session.turns) + 1,
                is_followup=False,
                question_text=next_q.question,
                question_category=next_q.category,
                difficulty=next_q.difficulty,
                expected_points=next_q.expected_concepts,
                resume_context_used=next_q.resume_context_used,
                adaptive_context=next_q.adaptive_context
            )
            self.db.add(next_turn)
        else:
            # Interview is completed! Generate final evaluation report.
            is_completed = True
            await self._finalize_session(session)

        await self.db.commit()
        if next_turn:
            await self.db.refresh(next_turn)
        await self.db.refresh(current_turn)

        return evaluation, current_turn, next_turn, is_completed

    async def _finalize_session(self, session: InterviewSession) -> FinalInterviewReport:
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

        report = await self.provider.generate_final_report(
            role_title=session.role_title,
            experience_level=session.experience_level,
            interview_type=session.interview_type,
            difficulty=session.difficulty,
            turns=turns_data,
            resume_text=session.resume_text,
            job_description=session.job_description
        )

        session.status = "completed"
        session.overall_score = report.overall_score
        session.readiness_level = report.readiness_level
        session.summary = report.summary
        session.strengths = report.strengths
        session.weaknesses = report.weaknesses
        session.hidden_weaknesses = [hw.model_dump() if hasattr(hw, 'model_dump') else hw for hw in report.hidden_weaknesses]
        session.recommended_topics = report.recommended_topics
        session.closing_advice = report.closing_advice

        return report

    async def finish_early(self, session_id: str) -> InterviewSession:
        """Manually complete an ongoing interview and compile report."""
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        await self._finalize_session(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
