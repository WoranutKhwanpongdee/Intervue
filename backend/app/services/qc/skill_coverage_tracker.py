import re
from typing import List, Set, Dict, Optional
from app.services.qc.qc_models import SkillCoverageReport

STANDARD_SKILL_KEYWORDS: Dict[str, List[str]] = {
    "Architecture & Systems": [
        "architecture", "system design", "distributed", "microservices", "invariants",
        "scalability", "load balancer", "high availability", "failover", "cap theorem"
    ],
    "Concurrency & Multithreading": [
        "concurrency", "race condition", "mutex", "lock", "deadlock", "thread",
        "async", "goroutine", "worker pool", "channel", "semaphore"
    ],
    "Database & Caching": [
        "database", "sql", "postgresql", "mysql", "redis", "cache", "nosql",
        "indexing", "acid", "replication", "partition", "sharding", "lru"
    ],
    "API & Security": [
        "api", "rest", "graphql", "grpc", "authentication", "jwt", "oauth",
        "idempotency", "rate limit", "circuit breaker", "cors", "rfc 7807"
    ],
    "Event Streaming & Queues": [
        "kafka", "rabbitmq", "event-driven", "pubsub", "message queue",
        "outbox", "cdc", "consumer lag", "idempotent consumer"
    ],
    "Leadership & STAR Behavioral": [
        "leadership", "conflict", "trade-off", "stakeholder", "mentoring",
        "incident", "ownership", "postmortem", "star", "failure"
    ]
}


class SkillCoverageTracker:
    """
    Tracks competency coverage across interview turns and identifies untested candidate skill areas.
    """

    @classmethod
    def extract_target_skills(
        cls,
        resume_text: Optional[str],
        job_description: Optional[str]
    ) -> List[str]:
        combined = f"{resume_text or ''} {job_description or ''}".lower()
        target_skills: Set[str] = set()

        for category, keywords in STANDARD_SKILL_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', combined):
                    target_skills.add(category)
                    break

        if not target_skills:
            target_skills = {"Architecture & Systems", "API & Security", "Database & Caching"}

        return sorted(list(target_skills))

    @classmethod
    def detect_covered_skills(
        cls,
        question_text: str,
        category: str,
        expected_concepts: List[str]
    ) -> List[str]:
        combined = f"{question_text} {category} {' '.join(expected_concepts)}".lower()
        covered: Set[str] = set()

        for domain, keywords in STANDARD_SKILL_KEYWORDS.items():
            if domain.lower() in category.lower():
                covered.add(domain)
                continue
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', combined):
                    covered.add(domain)
                    break

        return sorted(list(covered))

    @classmethod
    def evaluate_session_coverage(
        cls,
        target_skills: List[str],
        accumulated_covered_skills: List[str]
    ) -> SkillCoverageReport:
        target_set = set(target_skills)
        covered_set = set(accumulated_covered_skills).intersection(target_set)
        uncovered = sorted(list(target_set - covered_set))

        ratio = (len(covered_set) / len(target_set)) if target_set else 1.0
        recommended = uncovered[0] if uncovered else None

        return SkillCoverageReport(
            total_target_skills=len(target_set),
            covered_skills=sorted(list(covered_set)),
            uncovered_skills=uncovered,
            coverage_ratio=round(ratio, 2),
            recommended_focus_area=recommended
        )
