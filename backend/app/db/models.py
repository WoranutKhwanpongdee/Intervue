import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    role_title = Column(String(255), nullable=False)
    experience_level = Column(String(50), nullable=False)
    interview_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    num_questions = Column(Integer, default=5, nullable=False)
    resume_text = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
    status = Column(String(50), default="in_progress", nullable=False)  # in_progress, completed, abandoned
    
    # Final evaluation fields
    overall_score = Column(Float, nullable=True)
    readiness_level = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True, default=list)
    weaknesses = Column(JSON, nullable=True, default=list)
    recommended_topics = Column(JSON, nullable=True, default=list)
    closing_advice = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    turns = relationship(
        "QuestionTurn",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="QuestionTurn.turn_number"
    )


class QuestionTurn(Base):
    __tablename__ = "question_turns"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)
    is_followup = Column(Boolean, default=False, nullable=False)
    parent_turn_id = Column(String(36), nullable=True)

    question_text = Column(Text, nullable=False)
    question_category = Column(String(100), nullable=False, default="General")
    difficulty = Column(String(50), nullable=False, default="Medium")
    expected_points = Column(JSON, nullable=True, default=list)

    user_answer = Column(Text, nullable=True)
    answered_at = Column(DateTime, nullable=True)

    # Turn AI Evaluation
    technical_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    turn_score = Column(Float, nullable=True)
    
    feedback = Column(Text, nullable=True)
    key_positives = Column(JSON, nullable=True, default=list)
    areas_for_improvement = Column(JSON, nullable=True, default=list)
    sample_ideal_answer = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("InterviewSession", back_populates="turns")
