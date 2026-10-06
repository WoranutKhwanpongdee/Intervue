from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.llm import InterviewQuestion, AnswerEvaluation, FinalInterviewReport


SYSTEM_PROMPT = """You are Intervue, an elite, professional technical and executive interviewer.
Your style is rigorous, perceptive, fair, and encouraging. You conduct realistic interviews tailored specifically to the candidate's target role, experience level, and difficulty.
You avoid generic, cliché questions and ask deep, contextual, real-world questions.
Always respond in strict JSON adhering to the specified schema."""


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers supporting structured generation."""

    @abstractmethod
    async def generate_initial_question(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        resume_text: Optional[str] = None
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
        resume_text: Optional[str] = None
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
        resume_text: Optional[str] = None
    ) -> FinalInterviewReport:
        pass
