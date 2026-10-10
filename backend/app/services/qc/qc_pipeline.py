import logging
from typing import List, Optional, Tuple, Dict, Any

from app.schemas.llm import InterviewQuestion
from app.services.qc.qc_models import QuestionQCAudit, SkillCoverageReport
from app.services.qc.deduplication import DeduplicationChecker
from app.services.qc.ambiguity_detector import AmbiguityDetector
from app.services.qc.difficulty_calibrator import DifficultyCalibrator
from app.services.qc.skill_coverage_tracker import SkillCoverageTracker

logger = logging.getLogger("intervue.qc.pipeline")


class QuestionQualityControlPipeline:
    """
    Comprehensive Question Quality Control (QC) Pipeline:
    - Deduplication & Semantic Overlap Detection
    - Ambiguity & Clarity Scoring
    - Engineering Taxonomy Classification
    - Dynamic Difficulty Calibration
    - Target Skill Coverage Verification & Auto-Repair
    """

    @classmethod
    def audit_and_refine(
        cls,
        question: InterviewQuestion,
        previous_questions: List[str],
        target_skills: List[str],
        accumulated_skills: List[str],
        base_difficulty: str = "Medium",
        experience_level: str = "Senior",
        turn_scores: Optional[List[float]] = None
    ) -> Tuple[InterviewQuestion, QuestionQCAudit]:
        """
        Executes full quality control pipeline on a generated question.
        Returns the (possibly auto-repaired) question and its comprehensive QC audit report.
        """
        # 1. Deduplication Check
        is_dup, dup_score, matched_q = DeduplicationChecker.check_duplicate(
            candidate_question=question.question,
            previous_questions=previous_questions,
            threshold=0.65
        )

        # 2. Ambiguity & Clarity Audit
        clarity_score, ambiguity_flags, suggestions = AmbiguityDetector.audit_clarity(question.question)

        # 3. Dynamic Difficulty Calibration
        calibrated_diff = DifficultyCalibrator.calibrate_difficulty(
            base_difficulty=base_difficulty,
            experience_level=experience_level,
            turn_scores=turn_scores or []
        )

        # 4. Target Skill Coverage Audit
        covered_by_this_q = SkillCoverageTracker.detect_covered_skills(
            question_text=question.question,
            category=question.category,
            expected_concepts=question.expected_concepts
        )
        all_covered = list(set(accumulated_skills + covered_by_this_q))
        coverage_report = SkillCoverageTracker.evaluate_session_coverage(
            target_skills=target_skills,
            accumulated_covered_skills=all_covered
        )

        # 5. Composite Quality Score
        dedup_penalty = (dup_score * 40.0) if is_dup else (dup_score * 15.0)
        overall_qc_score = max(0.0, min(100.0, clarity_score - dedup_penalty))

        # 6. Auto-Repair & Enhancement Check
        is_auto_repaired = False
        repaired_text = question.question

        if not is_dup and clarity_score < 75.0 and len(question.question.split()) >= 8:
            # Auto-repair vague questions by appending concrete technical framing
            if not question.question.strip().endswith("?"):
                repaired_text = repaired_text.strip() + "?"
            
            if "trade-off" not in repaired_text.lower() and "how" in repaired_text.lower():
                repaired_text += " Explain the core trade-offs and edge-case handling in your design."
                is_auto_repaired = True
                clarity_score = min(92.0, clarity_score + 15.0)
                overall_qc_score = min(90.0, overall_qc_score + 15.0)
                suggestions.append("Auto-repaired: Appended trade-off and edge-case framing.")

        is_valid = (overall_qc_score >= 60.0) and not is_dup

        audit = QuestionQCAudit(
            is_valid=is_valid,
            overall_quality_score=round(overall_qc_score, 1),
            clarity_score=round(clarity_score, 1),
            duplicate_risk_score=dup_score,
            ambiguity_flags=ambiguity_flags,
            taxonomy_category=question.category,
            target_skills_covered=covered_by_this_q,
            missing_target_skills=coverage_report.uncovered_skills,
            calibrated_difficulty=calibrated_diff,
            refinement_suggestions=suggestions,
            is_auto_repaired=is_auto_repaired,
            repaired_question=repaired_text if is_auto_repaired else None
        )

        if is_auto_repaired:
            question.question = repaired_text
        question.difficulty = calibrated_diff

        logger.info(
            f"QC Audit Result: Quality={audit.overall_quality_score}, Clarity={audit.clarity_score}, "
            f"DupRisk={audit.duplicate_risk_score}, Valid={audit.is_valid}, Repaired={audit.is_auto_repaired}"
        )

        return question, audit
