import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from app.schemas.llm import InterviewQuestion, AnswerEvaluation, FinalInterviewReport
from app.services.llm.base import BaseLLMProvider, SYSTEM_PROMPT
from app.services.llm.gemini import clean_json_text

logger = logging.getLogger("intervue.llm.groq")


class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def _call_groq(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"{system_prompt} You must respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error(f"Groq API error ({resp.status_code}): {resp.text}")
                raise RuntimeError(f"Groq API returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_initial_question(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> InterviewQuestion:
        resume_context = f"\nCandidate Resume:\n{resume_text[:2500]}" if resume_text else ""
        job_context = f"\nTarget Job Description Requirements:\n{job_description[:2500]}" if job_description else ""
        prompt = f"""Generate the first question for a mock interview in JSON format.
Target Role: {role_title}
Experience Level: {experience_level}
Interview Mode: {interview_type} (Options: Technical, Behavioral, HR, Mixed, Job-specific)
Difficulty: {difficulty}
{job_context}
{resume_context}

Return JSON with fields:
question (str), category (str), difficulty (str), rationale (str), expected_concepts (list of str)"""
        raw = await self._call_groq(prompt)
        return InterviewQuestion(**json.loads(clean_json_text(raw)))

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
        prompt = f"""Evaluate candidate's answer to this interview question in JSON format.
Role: {role_title} ({experience_level})
Interview Mode: {interview_type}
Question: {question_text}
Expected Concepts: {json.dumps(expected_concepts)}
Candidate Answer: {user_answer}

Return JSON with fields:
technical_score (0-100 float), relevance_score (0-100 float), clarity_score (0-100 float), completeness_score (0-100 float), turn_score (0-100 float),
feedback (str), key_positives (list of str), areas_for_improvement (list of str), sample_ideal_answer (str),
requires_followup (bool), followup_reason (str or null)"""
        raw = await self._call_groq(prompt)
        return AnswerEvaluation(**json.loads(clean_json_text(raw)))

    async def generate_followup_question(
        self,
        role_title: str,
        experience_level: str,
        parent_question: str,
        user_answer: str,
        evaluation: AnswerEvaluation,
        difficulty: str
    ) -> InterviewQuestion:
        prompt = f"""Generate a focused follow-up question in JSON format.
Role: {role_title} ({experience_level})
Parent Question: {parent_question}
Candidate Answer: {user_answer}
Evaluation: {evaluation.feedback}
Reason: {evaluation.followup_reason or 'Probe trade-offs and edge cases'}

Return JSON with fields:
question (str), category (str), difficulty (str), rationale (str), expected_concepts (list of str)"""
        raw = await self._call_groq(prompt)
        return InterviewQuestion(**json.loads(clean_json_text(raw)))

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
        history = [f"Q: {t.get('question_text')}" for t in previous_turns]
        job_context = f"\nJob Requirements:\n{job_description[:2000]}" if job_description else ""
        prompt = f"""Generate question #{turn_number} of {total_questions} for a {role_title} ({experience_level}) interview.
Mode: {interview_type}, Difficulty: {difficulty}
{job_context}
Previous questions:
{chr(10).join(history)}
{f'Resume: {resume_text[:2000]}' if resume_text else ''}

Return JSON with fields:
question (str), category (str), difficulty (str), rationale (str), expected_concepts (list of str)"""
        raw = await self._call_groq(prompt)
        return InterviewQuestion(**json.loads(clean_json_text(raw)))

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
        history = []
        for idx, t in enumerate(turns, 1):
            history.append(f"Turn {idx}: Q: {t.get('question_text')} | Answer: {t.get('user_answer')} | Score: {t.get('turn_score')}")

        job_context = f"\nJob Context:\n{job_description[:2000]}" if job_description else ""
        prompt = f"""Generate final interview performance report for {role_title} ({experience_level}).
Mode: {interview_type}, Difficulty: {difficulty}
{job_context}
Transcript:
{chr(10).join(history)}

Return JSON with fields:
overall_score (0-100 float), readiness_level ("Needs Practice" | "Approaching Ready" | "Interview Ready" | "Strong Hire"),
summary (str), strengths (list of str), weaknesses (list of str), recommended_topics (list of str), closing_advice (str)"""
        raw = await self._call_groq(prompt)
        return FinalInterviewReport(**json.loads(clean_json_text(raw)))
