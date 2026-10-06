import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import InterviewSession, QuestionTurn
from app.schemas.interview import (
    CreateInterviewRequest,
    InterviewSessionDetail,
    InterviewSessionSummary,
    SubmitAnswerRequest,
    TurnEvaluationResponse,
    QuestionTurnResponse
)
from app.services.interview_engine import InterviewEngine

logger = logging.getLogger("intervue.routers.interviews")
router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("", response_model=InterviewSessionDetail, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: CreateInterviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start a new interview session and generate the initial question."""
    try:
        engine = InterviewEngine(db)
        session = await engine.create_session(payload)
        
        # Reload with turns
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session.id)
            .options(selectinload(InterviewSession.turns))
        )
        res = await db.execute(stmt)
        return res.scalar_one()
    except Exception as e:
        logger.error(f"Error creating interview session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize interview: {str(e)}"
        )


@router.get("", response_model=List[InterviewSessionSummary])
async def list_interviews(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List historical interview sessions ordered by creation date."""
    stmt = (
        select(InterviewSession)
        .options(selectinload(InterviewSession.turns))
        .order_by(desc(InterviewSession.created_at))
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(stmt)
    sessions = res.scalars().all()

    summaries = []
    for s in sessions:
        answered = len([t for t in s.turns if t.user_answer is not None])
        summaries.append(
            InterviewSessionSummary(
                id=s.id,
                role_title=s.role_title,
                experience_level=s.experience_level,
                interview_type=s.interview_type,
                difficulty=s.difficulty,
                num_questions=s.num_questions,
                status=s.status,
                overall_score=s.overall_score,
                readiness_level=s.readiness_level,
                created_at=s.created_at,
                updated_at=s.updated_at,
                answered_turns_count=answered,
                total_turns_count=len(s.turns)
            )
        )
    return summaries


@router.get("/{session_id}", response_model=InterviewSessionDetail)
async def get_interview_detail(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve an interview session with full question turns and evaluation details."""
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(selectinload(InterviewSession.turns))
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


@router.post("/{session_id}/turns/{turn_id}/answer", response_model=TurnEvaluationResponse)
async def submit_turn_answer(
    session_id: str,
    turn_id: str,
    payload: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db)
):
    """Submit candidate's answer for a question turn, evaluate it, and adaptively get the next turn."""
    try:
        engine = InterviewEngine(db)
        eval_result, turn, next_turn, is_completed = await engine.process_answer(
            session_id=session_id,
            turn_id=turn_id,
            answer=payload.answer
        )
        return TurnEvaluationResponse(
            evaluation=eval_result,
            turn=QuestionTurnResponse.model_validate(turn),
            next_question=QuestionTurnResponse.model_validate(next_turn) if next_turn else None,
            is_completed=is_completed
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answer: {str(e)}")


@router.post("/{session_id}/finish", response_model=InterviewSessionDetail)
async def finish_interview_early(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Conclude the interview early and generate final evaluation report."""
    try:
        engine = InterviewEngine(db)
        session = await engine.finish_early(session_id)
        return session
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error finishing interview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to conclude interview: {str(e)}")


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an interview session and its history."""
    stmt = select(InterviewSession).where(InterviewSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    await db.delete(session)
    await db.commit()
    return None
