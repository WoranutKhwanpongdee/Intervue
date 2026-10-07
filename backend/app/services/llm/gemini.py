import json
import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from app.schemas.llm import InterviewQuestion, AnswerEvaluation, FinalInterviewReport, ResumeAnalysis
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

    async def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        prompt = f"""Analyze this resume and extract structured profile data in JSON format.
Resume Text:
{resume_text[:6000]}

Return valid JSON adhering to this exact schema:
{{
  "candidate_name": "string or null",
  "inferred_role": "string (e.g. Senior Frontend Engineer, Full Stack Tech Lead)",
  "skills": ["skill 1", "skill 2", "skill 3", ...],
  "projects": [
    {{
      "name": "Project Name",
      "technologies": ["tech 1", "tech 2"],
      "description": "Brief summary of project role and achievements"
    }}
  ],
  "experiences": [
    {{
      "company": "Company Name",
      "role": "Position Title",
      "duration": "e.g. 2022 - Present",
      "highlights": ["highlight 1", "highlight 2"]
    }}
  ],
  "suggested_topics": ["Topic 1", "Topic 2", "Topic 3"]
}}"""
        raw = await self._call_gemini(prompt)
        cleaned = clean_json_text(raw)
        data = json.loads(cleaned)
        return ResumeAnalysis(**data)

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

CRITICAL: If candidate resume is provided, your question MUST directly refer to a specific project, technology stack, or challenge stated in their resume.

Return a valid JSON object matching this schema:
{{
  "question": "string (the interview question to ask candidate, citing their resume project/experience if provided)",
  "category": "string (e.g. Architecture, Core Fundamentals, Behavioral, Project Deep-Dive)",
  "difficulty": "{difficulty}",
  "rationale": "string (brief explanation why this question is suitable)",
  "expected_concepts": ["concept 1", "concept 2", "concept 3"],
  "resume_context_used": "string or null (mention which specific project/technology from resume this question investigates)"
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
Interview Mode: {interview_type}
Question: {question_text}
Expected Key Concepts: {json.dumps(expected_concepts)}
Candidate's Answer: {user_answer}

Rate strictly yet constructively for a {experience_level} professional.
Calculate technical_score (0-100), relevance_score (0-100), clarity_score (0-100), completeness_score (0-100).
turn_score should be a weighted combination: (technical * 0.4 + relevance * 0.25 + clarity * 0.15 + completeness * 0.2).
Set requires_followup to true only if the candidate answered partially or mentioned something intriguing that warrants a brief follow-up clarification, and total turns remaining permits it.

HIDDEN BLINDSPOT COACHING DIAGNOSIS:
Diagnose any latent communication or technical presentation blindspot in this specific response (e.g. 'You know the concept, but your answer lacks concrete production numbers or examples', 'You focused on what the tool does rather than explaining why you chose it over alternatives', or 'You became evasive on edge cases').

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
  "latent_blindspot": "string or null (perceptive coach diagnosis of unstated communication weakness)",
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
Evaluation Feedback: {evaluation.feedback}
Follow-up Intent: {evaluation.followup_reason or 'Probe trade-offs, scalability, or alternative approaches'}

Generate a sharp, realistic follow-up question that directly tests the candidate on what they said.
Return JSON:
{{
  "question": "string (the follow-up question)",
  "category": "Follow-up Deep Dive",
  "difficulty": "{difficulty}",
  "rationale": "string (why this follow-up tests candidate depth)",
  "expected_concepts": ["concept 1", "concept 2"],
  "resume_context_used": null,
  "adaptive_context": "string (brief note on how candidate's specific answer triggered this probe)"
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
        detailed_history = []
        for t in previous_turns:
            num = t.get('turn_number', '?')
            q = t.get('question_text', '')
            ans = (t.get('user_answer') or '')[:350]
            score = t.get('turn_score', 'N/A')
            positives = ", ".join(t.get('key_positives') or [])
            improvements = ", ".join(t.get('areas_for_improvement') or [])
            detailed_history.append(
                f"--- Turn #{num} ---\n"
                f"Question: {q}\n"
                f"Candidate's Answer: {ans}\n"
                f"Score: {score}/100\n"
                f"Demonstrated Strengths: {positives}\n"
                f"Identified Gaps: {improvements}"
            )
        
        history_text = "\n\n".join(detailed_history) if detailed_history else "None (first turn)"
        job_context = f"\nJob Description Requirements:\n{job_description[:2000]}" if job_description else ""
        resume_context = f"\nResume Highlights:\n{resume_text[:2500]}" if resume_text else ""

        prompt = f"""You are conducting a REAL-TIME ADAPTIVE technical interview.
Generate question #{turn_number} of {total_questions}.
Role: {role_title} ({experience_level})
Interview Mode: {interview_type} (Options: Technical, Behavioral, HR, Mixed, Job-specific)
Target Base Difficulty: {difficulty}
{job_context}
{resume_context}

=== FULL CANDIDATE PERFORMANCE & ANSWER MEMORY ===
{history_text}
===================================================

ADAPTIVE INTERVIEW RULES:
1. Candidate Memory & Continuity: Analyze the candidate's previous responses above. If they mentioned specific architectural patterns, libraries, or design decisions, weave those into new questions where natural.
2. Dynamic Calibration:
   - If candidate scored strongly (>80%) on previous questions, elevate the depth with higher-tier failure modes, distributed concurrency, or scale bottlenecks.
   - If candidate struggled (<60%) on previous questions, adapt by pivoting or testing foundational practical mastery without repeating the same exact prompt.
3. Resume Grounding: If resume highlights are present, ground this question in a specific project or toolchain from the resume.
4. Adaptive Context: In the 'adaptive_context' field, explicitly state in 1 concise sentence how their past answers/scores influenced this question.

Return JSON:
{{
  "question": "string",
  "category": "string",
  "difficulty": "string (Easy / Medium / Hard based on real-time adaptation)",
  "rationale": "string",
  "expected_concepts": ["concept 1", "concept 2"],
  "resume_context_used": "string or null",
  "adaptive_context": "string (e.g., 'Adapted: Candidate scored 90% on Q1; escalating to multi-region distributed failover')"
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

        prompt = f"""Generate an executive-grade Final Interview Evaluation Report with HIDDEN WEAKNESS & BLINDSPOT DETECTION.
Role: {role_title} ({experience_level})
Interview Mode: {interview_type}
Difficulty: {difficulty}
{f'Target Job Requirements: {job_description[:2000]}' if job_description else ''}
{f'Candidate Resume Profile: {resume_text[:2000]}' if resume_text else ''}
Full Interview Transcript & Scores:
{chr(10).join(turns_summary)}

CRITICAL COACHING TASK:
Identify 2-3 HIDDEN WEAKNESSES / BLINDSPOTS across the entire session:
Look beyond basic technical correctness. Spot subtle communication and thinking habits:
- 'What vs Why Bias' (Explaining what a technology does rather than why it was chosen)
- 'Lacks Concrete Examples' (Knows theoretical concepts but omits real-world examples, metrics, or architecture war stories)
- 'Follow-up Degradation' (Strong initial answers but becomes less specific or defensive during deep-dive follow-ups)
- 'Happy Path Assumption' (Overlooking failure modes, partial network partitions, timeouts, and degradation)
- 'Over-Engineering' (Proposing massive distributed tools where simple designs suffice)

Return JSON:
{{
  "overall_score": float (0-100 overall composite),
  "readiness_level": "Needs Practice | Approaching Ready | Interview Ready | Strong Hire",
  "summary": "string (comprehensive executive summary)",
  "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
  "weaknesses": ["specific gap 1", "specific gap 2"],
  "hidden_weaknesses": [
    {{
      "tag": "What vs Why Bias | Lacks Concrete Examples | Follow-up Degradation | Happy-Path Bias | Over-Engineering",
      "insight": "⚠️ You tend to describe what a technology does rather than explaining why you chose it over alternatives.",
      "evidence": "When asked about caching in Q2, you defined Redis operations without comparing memory overhead against in-memory LRU or explaining cache invalidation trade-offs.",
      "coaching_tip": "In real interviews, use the 'Why-First' rule: always name the trade-off or alternative you rejected before describing the tool."
    }}
  ],
  "recommended_topics": ["topic/framework/concept 1", "topic 2", "topic 3"],
  "closing_advice": "string (actionable closing advice)"
}}"""
        raw = await self._call_gemini(prompt)
        cleaned = clean_json_text(raw)
        data = json.loads(cleaned)
        return FinalInterviewReport(**data)
