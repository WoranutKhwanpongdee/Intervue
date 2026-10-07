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

REAL-TIME ADAPTIVE INTERVIEWING RULE:
You possess complete memory of all previous turns, including the candidate's exact answers, strengths demonstrated, and weaknesses identified.
1. Cross-Turn Context Continuity: Build upon technical architecture, tools, or philosophies the candidate brought up in earlier answers (e.g., if they discussed Redis caching in Q1, ask how their write-through invalidation in Q1 handles database replicas in Q2).
2. Performance-Based Dynamic Difficulty: If the candidate achieved high scores (>80%), escalate difficulty with rigorous failure scenarios, concurrency races, high throughput scale, or distributed trade-offs. If the candidate struggled (<60%), calibrate to adjacent practical fundamentals without repeating failed questions.
3. Adaptive Context: Always return an "adaptive_context" string stating explicitly how the candidate's previous response shaped the new question.

HIDDEN WEAKNESS & COACHING BLINDSPOT DETECTION RULE:
Act like a seasoned Staff Engineer & Executive Interview Coach. Do NOT just evaluate correctness; diagnose invisible behavioral, communication, and cognitive blindspots across answers:
- "What vs. Why" Bias: Explaining what a tool or pattern does rather than justifying WHY it was chosen over alternatives with real trade-offs.
- Concept Without Concrete Evidence: Knowing textbook theory (e.g., CAP theorem, Redis, ACID) but lacking concrete examples, metrics, or production war stories.
- Follow-up Degradation: Sounding confident on broad initial answers, but becoming vague or evasive when drilled on edge cases or failure modes.
- Happy-Path Bias: Assuming dependencies and networks never fail; overlooking retries, timeouts, and degradation.
- Over-Engineering Bias: Jumping straight to distributed systems or microservices for problems where a simpler monolithic approach is superior.

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
