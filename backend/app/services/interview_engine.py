import logging
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import InterviewSession, QuestionTurn
from app.schemas.interview import CreateInterviewRequest
from app.schemas.llm import AnswerEvaluation
from app.services.orchestrator.workflow_engine import InterviewWorkflowOrchestrator

logger = logging.getLogger("intervue.engine")


class InterviewEngine:
    """
    Unified façade interfacing FastAPI routers with the InterviewWorkflowOrchestrator.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.orchestrator = InterviewWorkflowOrchestrator(db)

    async def create_session(self, req: CreateInterviewRequest) -> InterviewSession:
        """Create new interview session and orchestrate initialization."""
        return await self.orchestrator.initialize_and_start(req)

    async def process_answer(
        self,
        session_id: str,
        turn_id: str,
        answer: str
    ) -> Tuple[AnswerEvaluation, QuestionTurn, Optional[QuestionTurn], bool]:
        """
        Evaluate candidate's answer and orchestrate next workflow transition
        (follow-up probe, next topic, or report finalization).
        """
        return await self.orchestrator.submit_and_evaluate(
            session_id=session_id,
            turn_id=turn_id,
            answer=answer
        )

    async def finish_early(self, session_id: str) -> InterviewSession:
        """Conclude an ongoing interview session early."""
        return await self.orchestrator.finish_early(session_id)

    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Rehydrate and resume an existing interview session."""
        return await self.orchestrator.resume_session(session_id)

    async def recover_session(self, session_id: str) -> InterviewSession:
        """Recover a failed or interrupted session back to a stable checkpoint."""
        return await self.orchestrator.recover_session(session_id)
