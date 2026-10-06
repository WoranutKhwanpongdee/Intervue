import json
import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from app.schemas.llm import InterviewQuestion, AnswerEvaluation, FinalInterviewReport
from app.services.llm.base import BaseLLMProvider, SYSTEM_PROMPT

logger = logging.getLogger("intervue.llm.gemini")


def clean_json_text(text: str) -> str:
    """Strip markdown code blocks or extra whitespace from LLM output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def _call_gemini(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json"
            }
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error(f"Gemini API error ({resp.status_code}): {resp.text}")
                raise RuntimeError(f"Gemini API returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            try:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return content
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse Gemini response structure: {data}")
                raise RuntimeError(f"Unexpected response structure from Gemini: {e}")

    async def generate_initial_question(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> InterviewQuestion:
        resume_context = f"\nCandidate Resume Highlights:\n{resume_text[:3000]}" if resume_text else ""
        job_context = f"\nTarget Job Description / Requirements:\n{job_description[:3000]}" if job_description else ""
        prompt = f"""Generate the first question for a mock interview.
Target Role: {role_title}
Experience Level: {experience_level}
Interview Mode: {interview_type} (Options: Technical, Behavioral, HR, Mixed, Job-specific)
Difficulty: {difficulty}
{job_context}
{resume_context}

Return a valid JSON object matching this schema:
{{
  "question": "string (the interview question to ask candidate)",
  "category": "string (e.g. Architecture, Core Fundamentals, Behavioral)",
  "difficulty": "{difficulty}",
  "rationale": "string (brief explanation why this question is suitable)",
  "expected_concepts": ["concept 1", "concept 2", "concept 3"]
}}"""
        raw = await self._call_gemini(prompt)
        cleaned = clean_json_text(raw)
        data = json.loads(cleaned)
        return InterviewQuestion(**data)

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
        prompt = f"""Evaluate candidate's answer to the following interview question.
Role: {role_title} ({experience_level})
Interview Type: {interview_type}
Question: {question_text}
Expected Key Concepts: {json.dumps(expected_concepts)}
Candidate's Answer: {user_answer}

Rate strictly yet constructively for a {experience_level} professional.
Calculate technical_score (0-100), relevance_score (0-100), clarity_score (0-100), completeness_score (0-100).
turn_score should be a weighted combination: (technical * 0.4 + relevance * 0.25 + clarity * 0.15 + completeness * 0.2).
Set requires_followup to true only if the candidate answered partially or mentioned something intriguing that warrants a brief follow-up clarification, and total turns remaining permits it.

Return a valid JSON object matching this schema:
{{
  "technical_score": float (0-100),
  "relevance_score": float (0-100),
  "clarity_score": float (0-100),
  "completeness_score": float (0-100),
  "turn_score": float (0-100),
  "feedback": "string (constructive breakdown of candidate's answer)",
  "key_positives": ["positive point 1", "positive point 2"],
  "areas_for_improvement": ["improvement point 1", "improvement point 2"],
  "sample_ideal_answer": "string (model answer illustrating ideal response)",
  "requires_followup": boolean,
  "followup_reason": "string or null"
}}"""
        raw = await self._call_gemini(prompt)
        cleaned = clean_json_text(raw)
        data = json.loads(cleaned)
        return AnswerEvaluation(**data)

    async def generate_followup_question(
        self,
        role_title: str,
        experience_level: str,
        parent_question: str,
        user_answer: str,
        evaluation: AnswerEvaluation,
        difficulty: str
    ) -> InterviewQuestion:
        prompt = f"""The candidate answered a question, but there is a nuance, edge case, or trade-off worth drilling deeper into.
Role: {role_title} ({experience_level})
Original Question: {parent_question}
Candidate's Previous Answer: {user_answer}
Evaluation Notes: {evaluation.feedback}
Followup Intent: {evaluation.followup_reason or 'Probe trade-offs, scalability, or alternative approaches'}

Generate a sharp, realistic follow-up question.
Return JSON:
{{
  "question": "string (the follow-up question)",
  "category": "Follow-up Deep Dive",
  "difficulty": "{difficulty}",
  "rationale": "string (why this follow-up tests candidate depth)",
  "expected_concepts": ["concept 1", "concept 2"]
}}"""
        raw = await self._call_gemini(prompt)
        cleaned = clean_json_text(raw)
        data = json.loads(cleaned)
        return InterviewQuestion(**data)

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
        history_summary = []
        for t in previous_turns:
            history_summary.append(f"Q: {t.get('question_text', '')} | Score: {t.get('turn_score', 'N/A')}")
        
        job_context = f"\nJob Description Requirements:\n{job_description[:2000]}" if job_description else ""
        prompt = f"""Generate question #{turn_number} of {total_questions} for this interview.
Role: {role_title} ({experience_level})
Interview Mode: {interview_type} (Options: Technical, Behavioral, HR, Mixed, Job-specific)
Difficulty: {difficulty}
{job_context}
Questions already covered:
{chr(10).join(history_summary)}

Ensure this question aligns with the selected mode and explores a complementary dimension.
{f'Resume Highlights: {resume_text[:2000]}' if resume_text else ''}

Return JSON:
{{
  "question": "string",
  "category": "string",
  "difficulty": "{difficulty}",
  "rationale": "string",
  "expected_concepts": ["concept 1", "concept 2"]
}}"""
        raw = await self._call_gemini(prompt)
        cleaned = clean_json_text(raw)
        data = json.loads(cleaned)
        return InterviewQuestion(**data)

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
        turns_summary = []
        for idx, t in enumerate(turns, 1):
            turns_summary.append(
                f"Turn {idx} ({'Follow-up' if t.get('is_followup') else 'Core'}): {t.get('question_text')}\n"
                f"Candidate Answer: {t.get('user_answer', 'No answer')}\n"
                f"Scores: Tech={t.get('technical_score')} Relevance={t.get('relevance_score')} Clarity={t.get('clarity_score')} Completeness={t.get('completeness_score')} Overall={t.get('turn_score')}\n"
                f"Feedback: {t.get('feedback', '')}\n"
            )

        prompt = f"""Generate an executive-grade Final Interview Evaluation Report.
Role: {role_title} ({experience_level})
Interview Mode: {interview_type}
Difficulty: {difficulty}
{f'Target Job Requirements: {job_description[:2000]}' if job_description else ''}
Full Interview Transcript & Scores:
{chr(10).join(turns_summary)}

Synthesize overall performance across all questions.
Return JSON:
{{
  "overall_score": float (0-100 overall composite),
  "readiness_level": "Needs Practice | Approaching Ready | Interview Ready | Strong Hire",
  "summary": "string (comprehensive executive summary)",
  "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
  "weaknesses": ["specific gap 1", "specific gap 2"],
  "recommended_topics": ["topic/framework/concept 1", "topic 2", "topic 3"],
  "closing_advice": "string (actionable closing advice)"
}}"""
        raw = await self._call_gemini(prompt)
        cleaned = clean_json_text(raw)
        data = json.loads(cleaned)
        return FinalInterviewReport(**data)
