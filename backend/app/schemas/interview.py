from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.llm import AnswerEvaluation, FinalInterviewReport, ResumeAnalysis, HiddenWeakness


class CreateInterviewRequest(BaseModel):
    role_title: str = Field(..., min_length=2, max_length=200, example="Senior Frontend Engineer")
    experience_level: str = Field(..., example="Senior")  # Junior, Mid, Senior, Lead, Principal
    interview_type: str = Field(..., example="Technical")  # Technical, Behavioral, HR, Mixed, Job-specific
    difficulty: str = Field(..., example="Medium")  # Easy, Medium, Hard
    num_questions: int = Field(default=5, ge=1, le=10, example=5)
    resume_text: Optional[str] = Field(default=None, max_length=25000)
    job_description: Optional[str] = Field(default=None, max_length=25000)


class QuestionTurnResponse(BaseModel):
    id: str
    session_id: str
    turn_number: int
    is_followup: bool
    parent_turn_id: Optional[str] = None
    question_text: str
    question_category: str
    difficulty: str
    expected_points: List[str] = []
    resume_context_used: Optional[str] = None
    adaptive_context: Optional[str] = None
    user_answer: Optional[str] = None
    answered_at: Optional[datetime] = None
    technical_score: Optional[float] = None
    relevance_score: Optional[float] = None
    clarity_score: Optional[float] = None
    completeness_score: Optional[float] = None
    turn_score: Optional[float] = None
    feedback: Optional[str] = None
    key_positives: List[str] = []
    areas_for_improvement: List[str] = []
    sample_ideal_answer: Optional[str] = None
    latent_blindspot: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=5, max_length=15000)


class TurnEvaluationResponse(BaseModel):
    evaluation: AnswerEvaluation
    turn: QuestionTurnResponse
    next_question: Optional[QuestionTurnResponse] = None
    is_completed: bool = False


class InterviewSessionSummary(BaseModel):
    id: str
    role_title: str
    experience_level: str
    interview_type: str
    difficulty: str
    num_questions: int
    status: str
    overall_score: Optional[float] = None
    readiness_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    answered_turns_count: int = 0
    total_turns_count: int = 0

    class Config:
        from_attributes = True


class InterviewSessionDetail(BaseModel):
    id: str
    role_title: str
    experience_level: str
    interview_type: str
    difficulty: str
    num_questions: int
    resume_text: Optional[str] = None
    job_description: Optional[str] = None
    status: str
    overall_score: Optional[float] = None
    readiness_level: Optional[str] = None
    summary: Optional[str] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    hidden_weaknesses: List[HiddenWeakness] = []
    recommended_topics: List[str] = []
    closing_advice: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    turns: List[QuestionTurnResponse] = []

    class Config:
        from_attributes = True


class ResumeParseResponse(BaseModel):
    filename: str
    extracted_text: str
    char_count: int
    analysis: Optional[ResumeAnalysis] = None
