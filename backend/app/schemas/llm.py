from typing import List, Optional
from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    question: str = Field(description="The interview question text to ask the candidate")
    category: str = Field(description="Domain/category, e.g., System Design, Architecture, Problem Solving, Soft Skills")
    difficulty: str = Field(description="Difficulty level: Easy, Medium, or Hard")
    rationale: str = Field(description="Why this question is relevant to the role and candidate level")
    expected_concepts: List[str] = Field(default_factory=list, description="Key concepts or technical facets expected in an ideal answer")


class AnswerEvaluation(BaseModel):
    technical_score: float = Field(ge=0, le=100, description="Technical accuracy score from 0 to 100")
    relevance_score: float = Field(ge=0, le=100, description="Relevance to question from 0 to 100")
    clarity_score: float = Field(ge=0, le=100, description="Clarity and communication quality score from 0 to 100")
    completeness_score: float = Field(ge=0, le=100, description="Depth and completeness score from 0 to 100")
    turn_score: float = Field(ge=0, le=100, description="Composite weighted score for this turn from 0 to 100")
    feedback: str = Field(description="Constructive, specific feedback on what worked and what was missing")
    key_positives: List[str] = Field(default_factory=list, description="Top positive aspects of candidate's answer")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Specific things to improve or clarify")
    sample_ideal_answer: str = Field(description="Concise model answer demonstrating how a top candidate would answer")
    requires_followup: bool = Field(default=False, description="Whether candidate's answer left an important ambiguity or gap that warrants a targeted follow-up")
    followup_reason: Optional[str] = Field(default=None, description="Reason why follow-up is warranted if any")


class FinalInterviewReport(BaseModel):
    overall_score: float = Field(ge=0, le=100, description="Overall weighted score 0 to 100")
    readiness_level: str = Field(description="Rating: 'Needs Practice', 'Approaching Ready', 'Interview Ready', or 'Strong Hire'")
    summary: str = Field(description="Executive summary of the candidate's interview performance")
    strengths: List[str] = Field(default_factory=list, description="Top candidate strengths demonstrated across turns")
    weaknesses: List[str] = Field(default_factory=list, description="Primary weaknesses or gaps to address")
    recommended_topics: List[str] = Field(default_factory=list, description="Specific topics or technologies to study next")
    closing_advice: str = Field(description="Practical, encouraging next steps for real-world interviews")
