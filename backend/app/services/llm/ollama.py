import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from app.schemas.llm import InterviewQuestion, AnswerEvaluation, FinalInterviewReport
from app.services.llm.base import BaseLLMProvider, SYSTEM_PROMPT
from app.services.llm.gemini import clean_json_text

logger = logging.getLogger("intervue.llm.ollama")


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def _call_ollama(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"{system_prompt} Always respond with a single valid JSON object."},
                {"role": "user", "content": prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.3}
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error(f"Ollama error ({resp.status_code}): {resp.text}")
                raise RuntimeError(f"Ollama returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["message"]["content"]

    async def generate_initial_question(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> InterviewQuestion:
        prompt = f"""Generate initial interview question for {role_title} ({experience_level}), mode: {interview_type}, difficulty: {difficulty}.
{f'Job Description: {job_description[:2000]}' if job_description else ''}
{f'Resume: {resume_text[:2000]}' if resume_text else ''}
Return JSON:
{{
  "question": "string",
  "category": "string",
  "difficulty": "{difficulty}",
  "rationale": "string",
  "expected_concepts": ["concept 1", "concept 2"]
}}"""
        raw = await self._call_ollama(prompt)
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
        prompt = f"""Evaluate answer for {role_title}. Mode: {interview_type}. Question: {question_text}. Expected: {expected_concepts}. Candidate answer: {user_answer}.
Return JSON:
{{
  "technical_score": float,
  "relevance_score": float,
  "clarity_score": float,
  "completeness_score": float,
  "turn_score": float,
  "feedback": "string",
  "key_positives": ["string"],
  "areas_for_improvement": ["string"],
  "sample_ideal_answer": "string",
  "requires_followup": boolean,
  "followup_reason": "string or null"
}}"""
        raw = await self._call_ollama(prompt)
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
        prompt = f"""Generate follow-up question for {role_title}. Original: {parent_question}. Answer: {user_answer}. Feedback: {evaluation.feedback}.
Return JSON:
{{
  "question": "string",
  "category": "Deep Dive",
  "difficulty": "{difficulty}",
  "rationale": "string",
  "expected_concepts": ["concept 1"]
}}"""
        raw = await self._call_ollama(prompt)
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
        prompt = f"""Generate question #{turn_number} of {total_questions} for {role_title} ({experience_level}), mode: {interview_type}, difficulty: {difficulty}.
{f'Job Description: {job_description[:2000]}' if job_description else ''}
Return JSON:
{{
  "question": "string",
  "category": "string",
  "difficulty": "{difficulty}",
  "rationale": "string",
  "expected_concepts": ["concept 1"]
}}"""
        raw = await self._call_ollama(prompt)
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
        prompt = f"""Generate final interview performance report for {role_title} ({experience_level}). Mode: {interview_type}. Turns completed: {len(turns)}.
Return JSON:
{{
  "overall_score": float,
  "readiness_level": "Needs Practice | Approaching Ready | Interview Ready | Strong Hire",
  "summary": "string",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommended_topics": ["string"],
  "closing_advice": "string"
}}"""
        raw = await self._call_ollama(prompt)
        return FinalInterviewReport(**json.loads(clean_json_text(raw)))
