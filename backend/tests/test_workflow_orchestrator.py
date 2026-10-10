import pytest
from app.schemas.interview import CreateInterviewRequest
from app.services.orchestrator.workflow_engine import InterviewWorkflowOrchestrator
from app.services.orchestrator.state_machine import InterviewState
from app.services.llm.mock import MockLLMProvider
from app.schemas.llm import AnswerEvaluation


@pytest.mark.asyncio
async def test_workflow_session_initialization(db_session, mock_provider):
    orchestrator = InterviewWorkflowOrchestrator(db_session, provider=mock_provider)

    req = CreateInterviewRequest(
        role_title="Senior Backend Engineer",
        experience_level="Senior",
        interview_type="Full-Loop",
        difficulty="Hard",
        num_questions=3,
        resume_text="Experienced Go and Redis engineer building payment gateways.",
        job_description="Looking for distributed systems architect."
    )

    session = await orchestrator.initialize_and_start(req)

    assert session.id is not None
    assert session.current_state == InterviewState.AWAITING_ANSWER.value
    assert session.status == "in_progress"
    assert session.current_round_stage == "Round 1: HR & Culture Fit"
    assert len(session.turns) == 1
    assert session.turns[0].turn_number == 1
    assert session.turns[0].user_answer is None
    assert session.turns[0].interviewer_persona == "Senior Talent Partner"


@pytest.mark.asyncio
async def test_workflow_answer_submission_and_advancement(db_session, mock_provider):
    orchestrator = InterviewWorkflowOrchestrator(db_session, provider=mock_provider)

    req = CreateInterviewRequest(
        role_title="Tech Lead",
        experience_level="Lead",
        interview_type="Full-Loop",
        difficulty="Medium",
        num_questions=3,
        resume_text="Tech Lead with microservices experience."
    )
    session = await orchestrator.initialize_and_start(req)
    turn_1 = session.turns[0]

    # Submit first answer
    eval_1, current_turn, next_turn, is_completed = await orchestrator.submit_and_evaluate(
        session_id=session.id,
        turn_id=turn_1.id,
        answer="I lead cross-functional architecture and ensure strong data consistency across services."
    )

    assert eval_1.turn_score is not None
    assert current_turn.user_answer is not None
    assert not is_completed
    assert next_turn is not None
    assert session.current_state == InterviewState.AWAITING_ANSWER.value


@pytest.mark.asyncio
async def test_workflow_deep_dive_probe_on_bluff(db_session):
    # Create custom mock provider that flags bluff
    class BluffMockProvider(MockLLMProvider):
        async def evaluate_answer(self, **kwargs):
            eval_res = await super().evaluate_answer(**kwargs)
            eval_res.bluff_detected = True
            eval_res.buzzwords_detected = ["RAG", "Vector Database"]
            eval_res.probing_rationale = "Stated tool name without chunking strategy."
            eval_res.requires_followup = True
            return eval_res

    orchestrator = InterviewWorkflowOrchestrator(db_session, provider=BluffMockProvider())

    req = CreateInterviewRequest(
        role_title="AI Engineer",
        experience_level="Senior",
        interview_type="Technical",
        difficulty="Hard",
        num_questions=3,
        resume_text="Built RAG with vector search."
    )
    session = await orchestrator.initialize_and_start(req)
    turn_1 = session.turns[0]

    eval_result, current_turn, followup_turn, is_completed = await orchestrator.submit_and_evaluate(
        session_id=session.id,
        turn_id=turn_1.id,
        answer="We used RAG and vector database for search."
    )

    assert eval_result.bluff_detected is True
    assert followup_turn is not None
    assert followup_turn.is_followup is True
    assert followup_turn.parent_turn_id == turn_1.id
    assert session.current_state == InterviewState.AWAITING_ANSWER.value


@pytest.mark.asyncio
async def test_workflow_completion_and_report_synthesis(db_session, mock_provider):
    orchestrator = InterviewWorkflowOrchestrator(db_session, provider=mock_provider)

    req = CreateInterviewRequest(
        role_title="Senior Frontend Engineer",
        experience_level="Senior",
        interview_type="Full-Loop",
        difficulty="Medium",
        num_questions=1,  # 1 question to complete quickly
        resume_text="React and Next.js expert."
    )
    session = await orchestrator.initialize_and_start(req)
    turn_1 = session.turns[0]

    # Submit final answer
    eval_result, current_turn, next_turn, is_completed = await orchestrator.submit_and_evaluate(
        session_id=session.id,
        turn_id=turn_1.id,
        answer="We optimized client-side rendering with server components and streaming hydration."
    )

    assert is_completed is True
    assert next_turn is None
    assert session.status == "completed"
    assert session.current_state == InterviewState.COMPLETED.value
    assert session.overall_score is not None
    assert len(session.round_evaluations) > 0
    assert session.hiring_committee_verdict is not None


@pytest.mark.asyncio
async def test_workflow_persistence_and_resume(db_session, mock_provider):
    orchestrator = InterviewWorkflowOrchestrator(db_session, provider=mock_provider)

    req = CreateInterviewRequest(
        role_title="Backend Engineer",
        experience_level="Senior",
        interview_type="Technical",
        difficulty="Medium",
        num_questions=3
    )
    session = await orchestrator.initialize_and_start(req)

    # Resume active session
    resume_result = await orchestrator.resume_session(session.id)

    assert resume_result["is_completed"] is False
    assert resume_result["current_state"] == InterviewState.AWAITING_ANSWER.value
    assert resume_result["active_turn"] is not None
    assert resume_result["active_turn"].id == session.turns[0].id


@pytest.mark.asyncio
async def test_workflow_recovery(db_session, mock_provider):
    orchestrator = InterviewWorkflowOrchestrator(db_session, provider=mock_provider)

    req = CreateInterviewRequest(
        role_title="DevOps Engineer",
        experience_level="Senior",
        interview_type="Technical",
        difficulty="Medium",
        num_questions=2
    )
    session = await orchestrator.initialize_and_start(req)

    # Simulate failure state
    session.current_state = InterviewState.FAILED.value
    await db_session.commit()

    # Recover session
    recovered_session = await orchestrator.recover_session(session.id)
    assert recovered_session.current_state == InterviewState.AWAITING_ANSWER.value
