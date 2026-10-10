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
    ResumeExperience,
    HiddenWeakness,
    SkillAssessment,
    DepthAuditItem,
    RoundEvaluation
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

        round_stage = "Round 1: HR Screening & Culture Fit" if interview_type in ["Full-Loop", "Mixed"] else None
        interviewer_persona = "Senior Talent Partner" if interview_type in ["Full-Loop", "Mixed"] else None

        return InterviewQuestion(
            question=custom_q,
            category=selected["category"] if not resume_context_used else "Resume Project Deep-Dive",
            difficulty=difficulty,
            rationale=f"Evaluates candidate's actual hands-on engineering experience and architectural ownership for a {experience_level} {role_title}.",
            expected_concepts=selected["expected_concepts"],
            resume_context_used=resume_context_used,
            round_stage=round_stage,
            interviewer_persona=interviewer_persona
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

        # Bluff & Superficial Buzzword Detection
        buzzword_dictionary = [
            "rag", "vector", "kafka", "redis", "microservices", "microservice",
            "event-driven", "circuit breaker", "graphql", "kubernetes", "k8s",
            "docker", "jwt", "oauth", "grpc", "cqrs", "sharding", "nosql",
            "outbox", "ebpf", "raft", "elasticsearch"
        ]
        lower_ans = user_answer.lower()
        detected_buzzwords = [bw.upper() for bw in buzzword_dictionary if re.search(r'\b' + bw + r'\b', lower_ans)]

        # Check if candidate dropped buzzwords without sufficient depth or reasoning
        bluff_detected = False
        probing_rationale = None
        requires_followup = False
        if detected_buzzwords and not is_followup:
            has_depth_indicators = any(term in lower_ans for term in ["chunk", "partition", "ttl", "metric", "latency", "scale", "qps", "lock", "tradeoff", "why", "because", "bench"])
            if not has_depth_indicators or word_count < 45:
                bluff_detected = True
                probing_rationale = f"Candidate referenced {', '.join(detected_buzzwords)} without detailing chunking/partitioning strategies, trade-offs, or production metrics."
                requires_followup = True
        elif not is_followup and (word_count >= 25) and (turn_number < total_questions) and (random.random() > 0.4):
            requires_followup = True

        # Micro latent blindspot detection for this turn
        latent_blindspot = None
        if bluff_detected:
            latent_blindspot = f"⚠️ You referenced {', '.join(detected_buzzwords)}, but your answer stayed high-level without explaining internal mechanics, data invariants, or evaluation criteria."
        elif word_count < 30:
            latent_blindspot = "⚠️ You know the concept, but your answer lacks concrete production examples or metrics."
        elif "why" not in lower_ans and "because" not in lower_ans and "trade" not in lower_ans:
            latent_blindspot = "⚠️ You tend to describe what a technology does rather than explaining why you chose it."
        elif is_followup:
            latent_blindspot = "⚠️ Your initial answers are strong, but you become less specific when asked follow-up questions."

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
            latent_blindspot=latent_blindspot,
            requires_followup=requires_followup,
            followup_reason=probing_rationale or ("Candidate mentioned high-level approach; probe deeper on edge case handling and scaling limits." if requires_followup else None),
            bluff_detected=bluff_detected,
            buzzwords_detected=detected_buzzwords,
            probing_rationale=probing_rationale
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
        # If bluff detector was triggered, craft a surgical depth probe!
        if evaluation.bluff_detected and evaluation.buzzwords_detected:
            bws = [bw.lower() for bw in evaluation.buzzwords_detected]
            if any(b in bws for b in ["rag", "vector"]):
                return InterviewQuestion(
                    question="You mentioned implementing a RAG pipeline. In production, retrieval precision and hallucination prevention are critical. How did you design your chunking strategy, choose your embedding dimensions, and evaluate retrieval faithfulness (e.g. using RAGAS or precision@k)?",
                    category="Depth Probe: RAG & Retrieval Internals",
                    difficulty=difficulty,
                    rationale="Validates genuine hands-on RAG experience by probing chunking boundaries, embedding trade-offs, and retrieval evaluation metrics.",
                    expected_concepts=["Chunking strategies (semantic vs fixed)", "Embedding dimensions & cosine distance", "Hybrid search (BM25 + dense)", "Evaluation metrics (Faithfulness / RAGAS)"],
                    resume_context_used=None,
                    adaptive_context="🔍 Depth Probe (Bluff Detector): Probing chunking, hybrid retrieval, and RAG evaluation metrics"
                )
            elif any(b in bws for b in ["kafka", "event-driven"]):
                return InterviewQuestion(
                    question="You highlighted using Kafka and event-driven pipelines. When scaling consumers under heavy load, how do you handle partition rebalancing without consumer lag spikes, and how do you guarantee idempotent message delivery?",
                    category="Depth Probe: Event-Driven & Messaging",
                    difficulty=difficulty,
                    rationale="Tests authentic messaging depth around consumer group rebalancing, offset commits, and deduplication.",
                    expected_concepts=["Consumer group rebalance protocol", "Transactional outbox", "Offset commit intervals", "Dead-letter queues"],
                    resume_context_used=None,
                    adaptive_context="🔍 Depth Probe (Bluff Detector): Probing Kafka partition rebalancing & consumer lag"
                )
            elif "redis" in bws:
                return InterviewQuestion(
                    question="You brought up Redis caching. When caching critical data with distributed locks, how do you handle lock lease expiration during unexpected garbage collection pauses to prevent split-brain double writes?",
                    category="Depth Probe: Distributed Invariants",
                    difficulty=difficulty,
                    rationale="Checks whether candidate understands Redlock safety caveats and GC pause clock drift.",
                    expected_concepts=["Lock lease expiry / TTL", "Fencing tokens", "GC pause clock drift", "Cache stampede lock lease"],
                    resume_context_used=None,
                    adaptive_context="🔍 Depth Probe (Bluff Detector): Probing Redis lock lease expiration & split-brain prevention"
                )
            else:
                bw_name = evaluation.buzzwords_detected[0]
                return InterviewQuestion(
                    question=f"You mentioned utilizing {bw_name}. Could you walk me through the internal mechanics, concrete failure scenarios you planned for, and how you measured its production impact?",
                    category=f"Depth Probe: {bw_name} Architecture",
                    difficulty=difficulty,
                    rationale=f"Validates authentic mastery of {bw_name} mechanics and trade-offs.",
                    expected_concepts=["Internal architecture mechanics", "Operational failure modes", "Production telemetry & metrics"],
                    resume_context_used=None,
                    adaptive_context=f"🔍 Depth Probe (Bluff Detector): Probing operational mechanics & metrics for {bw_name}"
                )

        # Standard adaptive follow-up
        words = [w.strip(".,;:()\"'") for w in user_answer.split() if len(w) > 4]
        key_term = words[0] if words else "your described architecture"
        return InterviewQuestion(
            question=f"Building directly on your response regarding '{key_term}': what happens if downstream dependency latency spikes or network partitions occur? How would you ensure data consistency and graceful degradation?",
            category="Adaptive Follow-up Deep Dive",
            difficulty=difficulty,
            rationale="Validates whether candidate understands operational resilience beyond happy-path implementations.",
            expected_concepts=["Graceful degradation", "Backpressure / Circuit breakers", "Fallback strategies", "Telemetry alerts"],
            resume_context_used=None,
            adaptive_context=f"Adapted from your answer: Probing resilience & edge cases around '{key_term}'"
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
        adaptive_context = None

        # Check last turn performance for real-time adaptation
        last_turn = previous_turns[-1] if previous_turns else None
        if last_turn:
            last_score = last_turn.get("turn_score") or 70
            last_ans = last_turn.get("user_answer") or ""
            words = [w.strip(".,;:()\"'") for w in last_ans.split() if len(w) > 4]
            pivot_concept = words[1] if len(words) > 1 else (words[0] if words else "your previous points")

            if last_score >= 80:
                difficulty = "Hard"
                adaptive_context = f"Adapted (High Score {round(last_score)}%): Escalating depth into distributed scale, race conditions, and failovers"
                custom_q = f"In your previous answer, you demonstrated strong intuition around '{pivot_concept}'. Let's push this further: {selected['question']} How would your design handle high concurrency and distributed data race conditions?"
            elif last_score < 60:
                difficulty = "Medium"
                adaptive_context = f"Adapted (Calibrating): Pivoting to practical real-world fundamentals after Q{last_turn.get('turn_number')}"
                custom_q = f"Let's explore another core pillar: {selected['question']}"
            else:
                adaptive_context = f"Adapted: Synthesizing concepts from Q{last_turn.get('turn_number')} response"
                custom_q = f"Connecting back to your approach on '{pivot_concept}': {selected['question']}"

        # Stage & Persona assignment for Full-Loop simulation
        round_stage = None
        interviewer_persona = None
        if interview_type in ["Full-Loop", "Mixed"]:
            if turn_number == 1:
                round_stage = "Round 1: HR Screening & Culture Fit"
                interviewer_persona = "Senior Talent Partner"
            elif turn_number == 2:
                round_stage = "Round 2: Technical Deep Dive & Systems"
                interviewer_persona = "Staff Systems Architect"
            elif turn_number == 3:
                round_stage = "Round 3: Behavioral & STAR Leadership"
                interviewer_persona = "Engineering Director"
            else:
                round_stage = "Round 4: Hiring Manager & Strategy"
                interviewer_persona = "Hiring Manager"

        return InterviewQuestion(
            question=custom_q,
            category=selected["category"] if not resume_context_used else "Resume Skill Deep-Dive",
            difficulty=difficulty,
            rationale=f"Evaluates candidate depth on {selected['category']} for {experience_level} caliber in {interview_type} mode.",
            expected_concepts=selected["expected_concepts"],
            resume_context_used=resume_context_used,
            adaptive_context=adaptive_context,
            round_stage=round_stage,
            interviewer_persona=interviewer_persona
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

        hidden_weaknesses = [
            HiddenWeakness(
                tag="What vs Why Bias",
                insight="⚠️ You tend to describe what a technology does rather than explaining why you chose it.",
                evidence="When discussing component design and data fetching, you explained how the APIs work rather than comparing memory/network trade-offs against lighter alternatives.",
                coaching_tip="Always follow the 'Why-First' rule: state the 1-2 alternatives you rejected and the specific constraint that made your choice the winner."
            ),
            HiddenWeakness(
                tag="Lacks Concrete Examples",
                insight="⚠️ You know the core concepts, but your answers lack concrete examples and production metrics.",
                evidence="Across architectural questions, explanations stayed mostly conceptual without citing throughput numbers (e.g. QPS, p99 latency) or specific deployment scale.",
                coaching_tip="Anchor every design with at least one measurable anchor (e.g., 'In a system handling 5k RPS, this prevents DB connection pool exhaustion')."
            ),
            HiddenWeakness(
                tag="Follow-up Degradation",
                insight="⚠️ Your technical answers are strong initially, but you become less specific when asked follow-up questions.",
                evidence="When probed on distributed failure recovery and latency spikes, your responses defaulted back to high-level summaries rather than walking through exact failure protocols.",
                coaching_tip="When a follow-up probe arrives, pause for 3 seconds and name the exact failure protocol (e.g. exponential backoff with jitter + dead-letter queue) step-by-step."
            )
        ]

        # Skill-by-skill competency map
        skill_map = [
            SkillAssessment(
                category="Core Architecture & Syntax",
                score=min(round(avg_score + 4, 1), 96.0),
                status="Mastered" if avg_score >= 80 else "Competent",
                observations=f"Solid grasp of fundamental design patterns and language invariants appropriate for a {experience_level} engineer.",
                confidence="High"
            ),
            SkillAssessment(
                category="API Design & Idempotency",
                score=min(round(avg_score - 2, 1), 92.0),
                status="Competent" if avg_score >= 70 else "Needs Practice",
                observations="Good conceptual handling of request lifecycles; could be more explicit regarding token lease timeouts and replay attacks.",
                confidence="High"
            ),
            SkillAssessment(
                category="Database & Caching Strategies",
                score=min(round(avg_score - 6, 1), 90.0),
                status="Competent" if avg_score >= 76 else "Needs Practice",
                observations="Familiar with Redis/SQL caching layers, but occasionally overlooks cache stampede mitigation and replica sync lag.",
                confidence="Medium"
            ),
            SkillAssessment(
                category="Problem Solving & Concurrency",
                score=min(round(avg_score + 1, 1), 95.0),
                status="Mastered" if avg_score >= 82 else "Competent",
                observations="Able to reason through multithreaded edge cases and deadlocks under probing.",
                confidence="Medium"
            ),
            SkillAssessment(
                category="Communication & Conviction",
                score=min(round(avg_score + 5, 1), 98.0),
                status="Mastered" if avg_score >= 78 else "Competent",
                observations="Structured articulation with clear terminology; benefited from pausing to organize thoughts before answering.",
                confidence="High"
            ),
            SkillAssessment(
                category="Distributed Telemetry & SRE",
                score=None,
                status="Insufficient Data",
                observations="OpenTelemetry, distributed tracing, and Prometheus metric alerts were not explicitly probed during this session.",
                confidence="Insufficient"
            )
        ]

        depth_audit = [
            DepthAuditItem(
                topic="RAG & Vector Search Pipeline",
                candidate_claim="Referenced building Retrieval-Augmented Generation (RAG) pipelines for semantic query answering.",
                verification_status="Verified Depth",
                probe_question="How did you design chunking boundaries, embedding dimensions, and evaluate retrieval faithfulness?",
                coach_observation="Candidate demonstrated genuine mastery by discussing hybrid BM25 + dense search and RAGAS precision metrics under follow-up probing."
            ),
            DepthAuditItem(
                topic="Distributed Mutex & Redis Caching",
                candidate_claim="Proposed Redis distributed locks for idempotent transaction management.",
                verification_status="Superficial / Probe Triggered",
                probe_question="How do you guarantee lock lease expiry doesn't cause split-brain updates during network partitions?",
                coach_observation="Initial answer lacked lock TTL lease parameters and fencing tokens; follow-up probe helped candidate clarify race boundaries."
            ),
            DepthAuditItem(
                topic="Event Streaming & Kafka Partitioning",
                candidate_claim="Mentioned Kafka event brokers for decoupling microservices.",
                verification_status="Verified Depth",
                probe_question="How do you handle partition rebalancing without consumer lag spikes?",
                coach_observation="Articulated sound understanding of consumer group offsets, transactional outbox pattern, and idempotent consumer workers."
            )
        ]

        round_evaluations = [
            RoundEvaluation(
                round_name="Round 1: HR Screening & Culture Fit",
                interviewer_persona="Senior Talent Partner",
                verdict="Strong Hire" if avg_score >= 80 else ("Hire" if avg_score >= 65 else "Lean Hire"),
                score=min(round(avg_score + 3, 1), 98.0),
                key_takeaway="Articulate communication, clear career motivations, and strong alignment with engineering culture."
            ),
            RoundEvaluation(
                round_name="Round 2: Technical & Systems Architecture",
                interviewer_persona="Staff Systems Architect",
                verdict="Strong Hire" if avg_score >= 82 else ("Hire" if avg_score >= 70 else "Lean Hire"),
                score=min(round(avg_score + 1, 1), 95.0),
                key_takeaway="Solid understanding of data invariants, concurrency races, and cache stampede trade-offs under probing."
            ),
            RoundEvaluation(
                round_name="Round 3: Behavioral & STAR Leadership",
                interviewer_persona="Engineering Director",
                verdict="Hire" if avg_score >= 75 else "Lean Hire",
                score=min(round(avg_score - 2, 1), 92.0),
                key_takeaway="Demonstrated empathy and ownership; could structure lessons from failure with tighter STAR metrics."
            ),
            RoundEvaluation(
                round_name="Round 4: Hiring Manager & Strategy",
                interviewer_persona="Hiring Manager",
                verdict="Strong Hire" if avg_score >= 80 else "Hire",
                score=min(round(avg_score + 2, 1), 96.0),
                key_takeaway="Sound business ROI intuition and pragmatic balance between engineering velocity and technical debt."
            )
        ]
        hiring_committee_verdict = "Strong Hire" if avg_score >= 85 else ("Hire" if avg_score >= 75 else ("Lean Hire" if avg_score >= 60 else "No Hire"))

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
            hidden_weaknesses=hidden_weaknesses,
            skill_map=skill_map,
            depth_audit=depth_audit,
            round_evaluations=round_evaluations,
            hiring_committee_verdict=hiring_committee_verdict,
            recommended_topics=recommended_topics,
            closing_advice=closing_advice
        )


MockLLMProvider = MockProvider

