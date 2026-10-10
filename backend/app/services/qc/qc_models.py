from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QuestionQCAudit(BaseModel):
    is_valid: bool = Field(default=True, description="Whether question meets production quality standards")
    overall_quality_score: float = Field(ge=0, le=100, default=90.0, description="Overall QC score (0-100)")
    clarity_score: float = Field(ge=0, le=100, default=92.0, description="Clarity & unambiguous phrasing score")
    duplicate_risk_score: float = Field(ge=0, le=1.0, default=0.0, description="Semantic overlap risk with past questions (0.0 - 1.0)")
    ambiguity_flags: List[str] = Field(default_factory=list, description="Specific ambiguities or vague phrasing identified")
    taxonomy_category: str = Field(default="Systems Architecture", description="Standardized engineering taxonomy classification")
    target_skills_covered: List[str] = Field(default_factory=list, description="Key candidate competencies assessed by this question")
    missing_target_skills: List[str] = Field(default_factory=list, description="Target competencies from resume/JD not yet evaluated in session")
    calibrated_difficulty: str = Field(default="Medium", description="Difficulty calibrated against candidate performance trajectory")
    refinement_suggestions: List[str] = Field(default_factory=list, description="Actionable enhancements if quality score < 80")
    is_auto_repaired: bool = Field(default=False, description="Whether question was automatically repaired/enhanced by QC pipeline")
    repaired_question: Optional[str] = Field(default=None, description="Enhanced version of the question if repair was applied")


class SkillCoverageReport(BaseModel):
    total_target_skills: int = 0
    covered_skills: List[str] = Field(default_factory=list)
    uncovered_skills: List[str] = Field(default_factory=list)
    coverage_ratio: float = 0.0
    recommended_focus_area: Optional[str] = None
