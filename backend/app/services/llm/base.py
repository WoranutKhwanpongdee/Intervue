from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.llm import InterviewQuestion, AnswerEvaluation, FinalInterviewReport, ResumeAnalysis


SYSTEM_PROMPT = """You are Intervue, an elite, professional technical and executive interviewer.
Your style is rigorous, perceptive, fair, and encouraging. You conduct realistic interviews tailored specifically to the candidate's target role, experience level, mode, and difficulty.

Support 5 Interview Modes:
1. Technical: Core fundamentals, system design, concurrency, architecture, algorithms, and practical debugging.
2. Behavioral: Teamwork, conflict resolution, ownership, STAR method (Situation, Task, Action, Result), leadership scenarios.
3. HR: Culture fit, career trajectory, motivations, compensation philosophy, work ethics, situational adaptability.
4. Mixed: Balanced cross-section of technical competence, problem solving, and behavioral maturity.
5. Job-specific: Tailored strictly to the exact target job description and candidate resume, focusing on required toolchains, domain-specific workflows, and real industry scenarios.

RESUME GROUNDING RULE:
Whenever a candidate's resume or project highlights are provided, you MUST ground questions and follow-ups in their specific stated projects, technologies, and achievements. Cite the specific project name or architectural challenge from their resume in your question prompt and explain what context was used.

Always respond in strict JSON adhering to the specified schema."""


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers supporting structured generation."""

    @abstractmethod
    async def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        """Parse raw resume text into structured skills, projects, experiences, and topics."""
        pass

    @abstractmethod
    async def generate_initial_question(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> InterviewQuestion:
        pass

    @abstractmethod
    async def evaluate_answer(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        question_text: str,
        expected_concepts: List[str],
        user_answer: str,
        is_followup: bool = False,
        turn_number: int = 1,
        total_questions: int = 5
    ) -> AnswerEvaluation:
        pass

    @abstractmethod
    async def generate_followup_question(
        self,
        role_title: str,
        experience_level: str,
        parent_question: str,
        user_answer: str,
        evaluation: AnswerEvaluation,
        difficulty: str
    ) -> InterviewQuestion:
        pass

    @abstractmethod
    async def generate_next_question(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        turn_number: int,
        total_questions: int,
        previous_turns: List[Dict[str, Any]],
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> InterviewQuestion:
        pass

    @abstractmethod
    async def generate_final_report(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        turns: List[Dict[str, Any]],
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> FinalInterviewReport:
        pass
