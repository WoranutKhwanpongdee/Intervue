import pytest
from app.schemas.llm import InterviewQuestion
from app.services.qc import (
    DeduplicationChecker,
    AmbiguityDetector,
    DifficultyCalibrator,
    SkillCoverageTracker,
    QuestionQualityControlPipeline,
    QuestionQCAudit
)


def test_deduplication_checker():
    q1 = "How do you ensure cache consistency in Redis when processing idempotent payment tokens under high concurrency?"
    q2 = "When processing idempotent payment tokens in Redis under concurrency, how do you handle cache consistency?"
    q3 = "Describe a time when you resolved a serious team conflict during an incident postmortem."

    is_dup, score, matched = DeduplicationChecker.check_duplicate(q2, [q1])
    assert is_dup is True
    assert score >= 0.65
    assert matched == q1

    is_dup_distinct, score_distinct, _ = DeduplicationChecker.check_duplicate(q3, [q1])
    assert is_dup_distinct is False
    assert score_distinct < 0.25


def test_ambiguity_detector_short_and_vague():
    vague_q = "Tell me about your system and what technology you like."
    clarity_score, flags, suggestions = AmbiguityDetector.audit_clarity(vague_q)

    assert clarity_score < 75.0
    assert len(flags) > 0
    assert any("Vague Phrasing" in f for f in flags)


def test_ambiguity_detector_high_quality_question():
    strong_q = "How do you ensure data consistency during network partitions when caching idempotent payment tokens in Redis without introducing cache stampedes?"
    clarity_score, flags, suggestions = AmbiguityDetector.audit_clarity(strong_q)

    assert clarity_score >= 85.0
    assert len(flags) == 0


def test_difficulty_calibrator_escalation_and_deescalation():
    # Strong candidate (> 85%) -> Escalates to Hard
    diff_escalated = DifficultyCalibrator.calibrate_difficulty(
        base_difficulty="Medium",
        experience_level="Senior",
        turn_scores=[88.0, 92.0]
    )
    assert diff_escalated == "Hard"

    # Struggling turn (< 60%) -> Calibrates to Medium fundamentals
    diff_calibrated = DifficultyCalibrator.calibrate_difficulty(
        base_difficulty="Hard",
        experience_level="Senior",
        turn_scores=[52.0]
    )
    assert diff_calibrated == "Medium"


def test_skill_coverage_tracker():
    resume = "Senior Go developer building PostgreSQL, Redis distributed caching, and microservices."
    jd = "Seeking Backend Engineer for high-throughput Kafka event streaming and API design."

    target_skills = SkillCoverageTracker.extract_target_skills(resume, jd)
    assert "Database & Caching" in target_skills
    assert "Event Streaming & Queues" in target_skills

    # Question covering Redis & Database
    covered_skills = SkillCoverageTracker.detect_covered_skills(
        question_text="How do you handle Redis cache stampedes and PostgreSQL transaction locks?",
        category="Database & Caching Topology",
        expected_concepts=["Redis Mutex", "PostgreSQL MVCC"]
    )
    assert "Database & Caching" in covered_skills

    report = SkillCoverageTracker.evaluate_session_coverage(target_skills, covered_skills)
    assert "Database & Caching" in report.covered_skills
    assert report.coverage_ratio > 0.0


def test_qc_pipeline_auto_repair_and_validation():
    # Test valid question
    good_q = InterviewQuestion(
        question="How do you design an idempotent checkout API handling 5000 RPS while preventing double-charges during client retry timeouts?",
        category="API Design & Invariants",
        difficulty="Medium",
        rationale="Tests idempotency and retry semantics",
        expected_concepts=["Idempotency keys", "Redis lock", "Transactional outbox"]
    )

    refined_q, audit = QuestionQualityControlPipeline.audit_and_refine(
        question=good_q,
        previous_questions=[],
        target_skills=["API & Security", "Database & Caching"],
        accumulated_skills=[],
        base_difficulty="Medium",
        experience_level="Senior",
        turn_scores=[85.0]
    )

    assert audit.is_valid is True
    assert audit.overall_quality_score >= 80.0
    assert "API & Security" in audit.target_skills_covered


def test_qc_pipeline_duplicate_detection():
    existing_q = "How do you handle Redis cache invalidation under high traffic?"
    dup_q = InterviewQuestion(
        question="How do you handle Redis cache invalidation under high traffic?",
        category="Database & Caching",
        difficulty="Medium",
        rationale="Test caching",
        expected_concepts=["Cache invalidation"]
    )

    _, audit = QuestionQualityControlPipeline.audit_and_refine(
        question=dup_q,
        previous_questions=[existing_q],
        target_skills=["Database & Caching"],
        accumulated_skills=["Database & Caching"]
    )

    assert audit.is_valid is False
    assert audit.duplicate_risk_score >= 0.65
