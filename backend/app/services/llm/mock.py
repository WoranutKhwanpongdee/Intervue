import random
import re
import logging
from typing import List, Dict, Any, Optional
from app.schemas.llm import (
    InterviewQuestion,
    AnswerEvaluation,
    FinalInterviewReport,
    ResumeAnalysis,
    ResumeProject,
    ResumeExperience
)
from app.services.llm.base import BaseLLMProvider

logger = logging.getLogger("intervue.llm.mock")

# Domain question banks for realistic mock interviews
DOMAIN_QUESTIONS = {
    "frontend": [
        {
            "question": "How does React's reconciliation algorithm and Fiber architecture optimize UI updates, and how would you diagnose unnecessary re-renders in a high-frequency dashboard?",
            "category": "React Internals & Performance",
            "expected_concepts": ["Virtual DOM diffing", "Fiber tree work loops", "React.memo / useMemo", "Profiler & flamegraph analysis", "State colocation"]
        },
        {
            "question": "Can you explain how Core Web Vitals (LCP, INP, CLS) impact web applications, and what architectural decisions you would take to achieve a sub-200ms INP?",
            "category": "Web Performance & Metrics",
            "expected_concepts": ["Interaction to Next Paint", "Main thread blocking tasks", "Code splitting & hydration", "Web Workers", "RequestIdleCallback"]
        },
        {
            "question": "Describe the security considerations when handling authentication tokens in single-page applications. Contrast HttpOnly cookies versus in-memory token storage with refresh token rotation.",
            "category": "Frontend Security",
            "expected_concepts": ["XSS vs CSRF", "SameSite attribute", "Token rotation", "Memory leaks in SPA", "Content Security Policy (CSP)"]
        },
        {
            "question": "Walk me through how you would architect a resilient, accessible design system component library supporting multiple themes, keyboard navigation, and zero runtime CSS overhead.",
            "category": "Design Systems & Architecture",
            "expected_concepts": ["WAI-ARIA compliance", "CSS variables / Tailwind tokens", "Compound components", "Tree shaking", "Polymorphic components"]
        }
    ],
    "backend": [
        {
            "question": "When designing a high-throughput payment processing API, how do you enforce idempotency, handle distributed transactions, and prevent race conditions?",
            "category": "Distributed Systems & APIs",
            "expected_concepts": ["Idempotency keys", "Two-phase commit or Saga pattern", "Optimistic vs Pessimistic locking", "Outbox pattern", "Dead-letter queues"]
        },
        {
            "question": "Explain how database indexing strategies (B-Trees vs LSM Trees vs Hash Indexes) impact read vs write throughput in relational vs append-only databases.",
            "category": "Databases & Storage",
            "expected_concepts": ["B+ Tree depth & page splits", "LSM compaction & SSTables", "Composite indexes", "Index selectivity", "Write amplification"]
        },
        {
            "question": "How would you design a rate limiter supporting millions of requests per minute with sliding window counters, and how do you ensure high availability across multiple availability zones?",
            "category": "System Design & Concurrency",
            "expected_concepts": ["Sliding window counter algorithm", "Redis / memory cluster", "Lua script atomicity", "Fail-open vs fail-closed", "Local cache fallback"]
        },
        {
            "question": "Discuss strategies for managing database migrations in zero-downtime blue/green deployments where old and new application instances run simultaneously.",
            "category": "DevOps & Reliability",
            "expected_concepts": ["Expand and Contract pattern", "Backward compatibility", "Non-blocking index creation", "Feature flags", "Dual writing"]
        }
    ],
    "general": [
        {
            "question": "Can you describe a time when you disagreed with a major architectural decision proposed by your team lead or peer? How did you approach the disagreement, and what was the outcome?",
            "category": "Collaboration & Conflict Resolution",
            "expected_concepts": ["Data-driven reasoning", "Empathy & active listening", "Proof of concept demonstration", "Disagree and commit", "Team retrospective"]
        },
        {
            "question": "Tell me about a complex project where technical debt significantly hindered feature delivery. How did you quantify the debt, prioritize remediation, and communicate the value to non-technical stakeholders?",
            "category": "Engineering Leadership & Pragmatism",
            "expected_concepts": ["Refactoring roadmap", "Measuring delivery cycle time", "Business impact framing", "Incremental migration", "Automated testing safety net"]
        },
        {
            "question": "Describe a production incident where an unforeseen bug caused system degradation. Walk me through your triage, root cause analysis, mitigation, and blameless post-mortem process.",
            "category": "Incident Response & Reliability",
            "expected_concepts": ["Rollback vs patch decision", "Observability & telemetry", "Root cause 5-Whys", "Action items & prevention", "Blameless post-mortem culture"]
        }
    ],
    "hr": [
        {
            "question": "What specifically motivated you to consider this transition, and what key criteria are you looking for in your next team and engineering culture?",
            "category": "Career Motivation & Culture Fit",
            "expected_concepts": ["Clear career trajectory", "Impact and ownership", "Team collaboration values", "Healthy feedback culture"]
        },
        {
            "question": "Tell me about a time you had to manage conflicting priorities and tight deadlines with competing stakeholders. How did you communicate trade-offs and manage expectations?",
            "category": "Work Ethic & Stakeholder Alignment",
            "expected_concepts": ["Prioritization matrix", "Proactive transparent communication", "Escalation protocols", "Outcome delivery"]
        },
        {
            "question": "How do you handle feedback or criticism when a project or pull request you invested heavily in needs to be significantly changed or cancelled?",
            "category": "Adaptability & Growth Mindset",
            "expected_concepts": ["Emotional maturity", "Objective problem orientation", "Constructive reflection", "Team first mentality"]
        }
    ],
    "job_specific": [
        {
            "question": "Based on the specific requirements for this target role, walk me through how your past hands-on experience directly matches the primary deliverables and tech stack expected in the first 90 days.",
            "category": "Role Deliverables & Tech Stack Fit",
            "expected_concepts": ["Direct tooling proficiency", "Onboarding ramp-up plan", "Domain problem familiarity", "Measurable project milestones"]
        },
        {
            "question": "Describe a production feature or system you built that closely mirrors the core domain challenges of this position. What were the toughest architectural constraints you solved?",
            "category": "Domain Scenario Problem Solving",
            "expected_concepts": ["Specific domain mechanics", "Performance constraints", "System integration", "Maintainability and testing"]
        }
    ]
}

KNOWN_SKILLS_KEYWORDS = [
    "TypeScript", "JavaScript", "Python", "Go", "Golang", "Java", "C++", "Rust",
    "React", "Next.js", "Vue", "Angular", "Tailwind CSS", "Node.js", "Express", "FastAPI", "Django", "Flask",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "DynamoDB",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "CI/CD", "GitHub Actions",
    "GraphQL", "REST API", "gRPC", "Kafka", "RabbitMQ", "Microservices", "System Design"
]


class MockProvider(BaseLLMProvider):
    """Realistic deterministic provider useful for testing and offline environments."""

    def _select_domain(self, role_title: str, interview_type: str) -> str:
        itype = interview_type.lower()
        if "hr" in itype:
            return "hr"
        if "job" in itype:
            return "job_specific"
        if "behavioral" in itype or "leadership" in itype:
            return "general"
        if "mixed" in itype:
            return "general"
        
        role = role_title.lower()
        if any(kw in role for kw in ["front", "react", "vue", "web", "ui", "javascript", "typescript"]):
            return "frontend"
        if any(kw in role for kw in ["back", "python", "golang", "java", "api", "data", "cloud", "system"]):
            return "backend"
        return "frontend"

    async def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        """Heuristic analysis of resume text to extract skills and project highlights."""
        text_lower = resume_text.lower()
        
        # Detect skills
        detected_skills = []
        for skill in KNOWN_SKILLS_KEYWORDS:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                detected_skills.append(skill)
        
        if not detected_skills:
            detected_skills = ["TypeScript", "React", "Node.js", "PostgreSQL", "Docker"]

        # Parse projects or synthesize from text
        projects = [
            ResumeProject(
                name="High-Throughput Web Application",
                technologies=detected_skills[:3],
                description="Engineered scalable frontend/backend architecture handling core user workflows and state synchronization."
            ),
            ResumeProject(
                name="Distributed API & Microservices Platform",
                technologies=detected_skills[2:6] if len(detected_skills) >= 6 else detected_skills,
                description="Designed resilient service endpoints with database caching, telemetry, and automated deployment pipelines."
            )
        ]

        experiences = [
            ResumeExperience(
                company="Tech Solutions Inc.",
                role="Senior Software Engineer",
                duration="2022 - Present",
                highlights=[
                    f"Spearheaded development of core features using {', '.join(detected_skills[:3])}.",
                    "Reduced latency and improved system reliability through code profiling and test automation."
                ]
            )
        ]

        suggested_topics = [
            f"Deep-dive into {detected_skills[0]} architectural patterns" if detected_skills else "System Architecture",
            f"State management, caching with {detected_skills[1] if len(detected_skills) > 1 else 'Redis'}",
            "Handling distributed edge cases and operational failures"
        ]

        return ResumeAnalysis(
            candidate_name="Candidate",
            inferred_role="Senior Software Engineer",
            skills=detected_skills[:12],
            projects=projects,
            experiences=experiences,
            suggested_topics=suggested_topics
        )

    async def generate_initial_question(
        self,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> InterviewQuestion:
        domain = self._select_domain(role_title, interview_type)
        pool = DOMAIN_QUESTIONS.get(domain, DOMAIN_QUESTIONS["general"])
        selected = pool[0]
        
        resume_context_used = None
        custom_q = selected["question"]

        if resume_text and len(resume_text) > 30:
            analysis = await self.analyze_resume(resume_text)
            top_skill = analysis.skills[0] if analysis.skills else "your primary stack"
            top_proj = analysis.projects[0].name if analysis.projects else "your recent production project"
            
            custom_q = f"In your resume, you highlighted working on '{top_proj}' using {top_skill}. Walk me through a challenging architectural decision you made on this project, and how you handled unexpected edge cases or performance bottlenecks?"
            resume_context_used = f"Grounded in: {top_proj} ({top_skill})"
        elif job_description and len(job_description) > 30 and domain == "job_specific":
            custom_q = f"Looking at the core requirements for this position: {selected['question']}"

        return InterviewQuestion(
            question=custom_q,
            category=selected["category"] if not resume_context_used else "Resume Project Deep-Dive",
            difficulty=difficulty,
            rationale=f"Evaluates candidate's actual hands-on engineering experience and architectural ownership for a {experience_level} {role_title}.",
            expected_concepts=selected["expected_concepts"],
            resume_context_used=resume_context_used
        )

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
        words = user_answer.strip().split()
        word_count = len(words)
        
        matched_concepts = []
        answer_lower = user_answer.lower()
        for concept in expected_concepts:
            tokens = [t.lower() for t in concept.split() if len(t) > 3]
            if any(t in answer_lower for t in tokens):
                matched_concepts.append(concept)
        
        if word_count < 20:
            base_tech = 45.0
            base_rel = 55.0
            base_clar = 50.0
            base_comp = 35.0
            feedback = "Your answer was very brief. To demonstrate seniority, elaborate on practical mechanics, edge cases, and real-world trade-offs."
        elif word_count < 60:
            base_tech = 68.0 + min(len(matched_concepts) * 5, 15)
            base_rel = 75.0
            base_clar = 72.0
            base_comp = 65.0
            feedback = "Solid baseline explanation, but could go deeper into operational consequences and concrete examples from your past projects."
        else:
            base_tech = 78.0 + min(len(matched_concepts) * 5, 18)
            base_rel = 85.0
            base_clar = 82.0
            base_comp = 80.0
            feedback = "Well-articulated response with clear practical intuition. Good demonstration of core principles and problem structure."

        tech = min(max(base_tech, 30.0), 96.0)
        rel = min(max(base_rel, 40.0), 98.0)
        clar = min(max(base_clar, 40.0), 95.0)
        comp = min(max(base_comp, 30.0), 94.0)
        composite = round(tech * 0.4 + rel * 0.25 + clar * 0.15 + comp * 0.2, 1)

        positives = [
            f"Addressed key aspects: {', '.join(matched_concepts[:2]) if matched_concepts else 'general problem context'}",
            "Communicated the thought process in a structured manner"
        ]
        
        missing = [c for c in expected_concepts if c not in matched_concepts]
        improvements = [
            f"Discuss: {missing[0]}" if missing else "Mention operational metrics and monitoring",
            "Explicitly weigh trade-offs and alternative approaches"
        ]

        sample_answer = (
            f"In my experience with {role_title} architectures, I approached this by establishing clear invariant boundaries. "
            f"First, focusing on {expected_concepts[0] if expected_concepts else 'fundamental invariants'}, "
            f"ensuring resilience through {expected_concepts[1] if len(expected_concepts) > 1 else 'defensive architecture'}, "
            f"and continuously verifying behavior with comprehensive telemetry."
        )

        requires_followup = not is_followup and (word_count >= 25) and (turn_number < total_questions) and (random.random() > 0.4)

        return AnswerEvaluation(
            technical_score=tech,
            relevance_score=rel,
            clarity_score=clar,
            completeness_score=comp,
            turn_score=composite,
            feedback=feedback,
            key_positives=positives,
            areas_for_improvement=improvements,
            sample_ideal_answer=sample_answer,
            requires_followup=requires_followup,
            followup_reason="Candidate mentioned high-level approach; probe deeper on edge case handling and scaling limits." if requires_followup else None
        )

    async def generate_followup_question(
        self,
        role_title: str,
        experience_level: str,
        parent_question: str,
        user_answer: str,
        evaluation: AnswerEvaluation,
        difficulty: str
    ) -> InterviewQuestion:
        return InterviewQuestion(
            question="Building on your previous answer, what happens if traffic spikes 10x or network latency degrades significantly? What specific failure modes would emerge and how would you mitigate them?",
            category="Failure Modes & Scale Deep Dive",
            difficulty=difficulty,
            rationale="Validates whether candidate understands operational resilience beyond happy-path implementations.",
            expected_concepts=["Graceful degradation", "Backpressure / Circuit breakers", "Fallback strategies", "Telemetry alerts"],
            resume_context_used=None
        )

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
        domain = self._select_domain(role_title, interview_type)
        pool = DOMAIN_QUESTIONS.get(domain, DOMAIN_QUESTIONS["general"])
        idx = (turn_number - 1) % len(pool)
        selected = pool[idx]

        custom_q = selected["question"]
        resume_context_used = None

        if resume_text and len(resume_text) > 30 and turn_number == 2:
            analysis = await self.analyze_resume(resume_text)
            if len(analysis.skills) >= 2:
                s2 = analysis.skills[1]
                custom_q = f"You also listed proficiency with '{s2}' on your resume. How have you applied {s2} in production to solve concurrency, state management, or data consistency issues?"
                resume_context_used = f"Grounded in: Resume Skill '{s2}'"

        return InterviewQuestion(
            question=custom_q,
            category=selected["category"] if not resume_context_used else "Resume Skill Deep-Dive",
            difficulty=difficulty,
            rationale=f"Evaluates candidate depth on {selected['category']} for {experience_level} caliber in {interview_type} mode.",
            expected_concepts=selected["expected_concepts"],
            resume_context_used=resume_context_used
        )

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
        scores = [t.get("turn_score", 70.0) for t in turns if t.get("turn_score") is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 75.0

        if avg_score >= 85:
            readiness = "Strong Hire"
            summary = f"Exceptional interview performance. Demonstrated deep domain mastery, crisp structured communication, and strong architectural instincts appropriate for a {experience_level} {role_title}."
        elif avg_score >= 75:
            readiness = "Interview Ready"
            summary = f"Strong performance overall. Displayed competent fundamentals and sound reasoning. With minor polish on edge case articulation, the candidate is well-positioned for competitive rounds."
        elif avg_score >= 60:
            readiness = "Approaching Ready"
            summary = f"Promising foundation with solid conceptual familiarity, but answers occasionally lacked concrete depth or omitted critical system failure modes."
        else:
            readiness = "Needs Practice"
            summary = f"The candidate showed enthusiasm but struggled to deliver comprehensive technical depth required for a {experience_level} level interview."

        strengths = [
            f"Clear structured thinking when tackling {interview_type} prompts",
            "Sound conceptual foundation in core architectural trade-offs",
            "Professional, candid communication style"
        ]
        weaknesses = [
            "Could proactively detail operational observability and metric telemetry",
            "Need deeper articulation of distributed failure modes and edge cases"
        ]
        recommended_topics = [
            "System Design & Distributed Data Patterns (Saga, Outbox, CDC)",
            "Performance Profiling, Bottleneck Analysis, and Benchmarking",
            "Resilience Engineering: Circuit Breakers, Bulkheads, and Rate Limiters"
        ]
        closing_advice = "Focus on framing your answers with the STAR method for behavioral context or Requirement-Design-Tradeoffs for technical discussions. Lead with strong convictions, backed by concrete numbers and previous architectural lessons."

        return FinalInterviewReport(
            overall_score=avg_score,
            readiness_level=readiness,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            recommended_topics=recommended_topics,
            closing_advice=closing_advice
        )
