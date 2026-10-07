from typing import List, Optional
from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    question: str = Field(description="The interview question text to ask the candidate")
    category: str = Field(description="Domain/category, e.g., System Design, Architecture, Problem Solving, Soft Skills")
    difficulty: str = Field(description="Difficulty level: Easy, Medium, or Hard")
    rationale: str = Field(description="Why this question is relevant to the role, resume projects, and candidate level")
    expected_concepts: List[str] = Field(default_factory=list, description="Key concepts or technical facets expected in an ideal answer")
    resume_context_used: Optional[str] = Field(default=None, description="Specific project, skill, or experience from resume that inspired this question")
    adaptive_context: Optional[str] = Field(default=None, description="Explanation of how this question adapted in real-time based on candidate's previous answers, strengths, or gaps")


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
    latent_blindspot: Optional[str] = Field(default=None, description="Perceptive coaching insight on invisible communication/cognitive pattern in this turn")
    requires_followup: bool = Field(default=False, description="Whether candidate's answer left an important ambiguity or gap that warrants a targeted follow-up")
    followup_reason: Optional[str] = Field(default=None, description="Reason why follow-up is warranted if any")


class HiddenWeakness(BaseModel):
    tag: str = Field(description="Short classification tag, e.g., 'What vs Why Bias', 'Lacks Concrete Evidence', 'Follow-up Degradation', 'Theoretical vs Practical'")
    insight: str = Field(description="Perceptive coach diagnosis of the blindspot, e.g., 'You know the concept, but your answers lack concrete examples.'")
    evidence: str = Field(description="Specific turn, phrasing, or pattern observed across answers that revealed this blindspot")
    coaching_tip: str = Field(description="Actionable rule or mental model to eliminate this blindspot in real interviews")


class ResumeProject(BaseModel):
    name: str = Field(description="Project name or key initiative")
    technologies: List[str] = Field(default_factory=list, description="Tech stack and tools used")
    description: str = Field(description="Summary of project impact and architecture")


class ResumeExperience(BaseModel):
    company: str = Field(description="Company or organization name")
    role: str = Field(description="Position or job title")
    duration: Optional[str] = Field(default=None, description="Time period or years")
    highlights: List[str] = Field(default_factory=list, description="Key technical accomplishments")


class ResumeAnalysis(BaseModel):
    candidate_name: Optional[str] = Field(default=None, description="Candidate name")
    inferred_role: Optional[str] = Field(default=None, description="Inferred role title and level")
    skills: List[str] = Field(default_factory=list, description="List of technical skills, languages, and frameworks")
    projects: List[ResumeProject] = Field(default_factory=list, description="Key projects parsed from resume")
    experiences: List[ResumeExperience] = Field(default_factory=list, description="Work experiences parsed from resume")
    suggested_topics: List[str] = Field(default_factory=list, description="Recommended interview topics tailored to this resume")


class FinalInterviewReport(BaseModel):
    overall_score: float = Field(ge=0, le=100, description="Overall weighted score 0 to 100")
    readiness_level: str = Field(description="Rating: 'Needs Practice', 'Approaching Ready', 'Interview Ready', or 'Strong Hire'")
    summary: str = Field(description="Executive summary of the candidate's interview performance")
    strengths: List[str] = Field(default_factory=list, description="Top candidate strengths demonstrated across turns")
    weaknesses: List[str] = Field(default_factory=list, description="Primary weaknesses or gaps to address")
    hidden_weaknesses: List[HiddenWeakness] = Field(default_factory=list, description="Latent behavioral and communication blindspots detected across candidate responses")
    recommended_topics: List[str] = Field(default_factory=list, description="Specific topics or technologies to study next")
    closing_advice: str = Field(description="Practical, encouraging next steps for real-world interviews")
