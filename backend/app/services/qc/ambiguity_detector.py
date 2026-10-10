import re
from typing import List, Tuple

VAGUE_PATTERNS = [
    (r'\btell (me|us) about (your|a) (code|system|project)\b', "Overly generic prompt without specific technical constraints"),
    (r'\bwhat is your (favorite|preferred) technology\b', "Subjective preference instead of technical evaluation"),
    (r'\bdo you (know|understand|have experience with)\b', "Binary yes/no question without probing mechanics"),
    (r'\bhow do you (code|program|do software)\b', "Indeterminate scope lacking system or architectural boundaries"),
    (r'\bexplain everything about\b', "Unbounded question scope"),
]

STRONG_EVALUATION_CUES = [
    "how do you ensure",
    "how would you design",
    "trade-offs between",
    "under high concurrency",
    "network partition",
    "cache invalidation",
    "data consistency",
    "failure modes",
    "walk me through",
    "describe a time when",
    "what metrics",
    "invariants",
    "concurrency",
    "race condition",
    "bottleneck",
    "idempotency"
]


class AmbiguityDetector:
    """
    Detects vague, ambiguous, or unbounded interview questions and measures clarity.
    """

    @classmethod
    def audit_clarity(cls, question_text: str) -> Tuple[float, List[str], List[str]]:
        """
        Returns:
            clarity_score (float): 0 to 100.
            ambiguity_flags (List[str]): List of detected issues.
            suggestions (List[str]): Improvement recommendations.
        """
        flags: List[str] = []
        suggestions: List[str] = []
        score = 100.0

        words = question_text.split()
        word_count = len(words)

        # Length checks
        if word_count < 12:
            score -= 30.0
            flags.append("Question is too short (< 12 words) and lacks sufficient context or technical constraints.")
            suggestions.append("Add explicit system constraints, workload scale (e.g. QPS), or failure scenarios.")
        elif word_count > 95:
            score -= 20.0
            flags.append("Question is overly long (> 95 words) and may confuse the candidate.")
            suggestions.append("Split multi-part prompts into crisp, focused architectural questions.")

        # Vague pattern checks
        lower_text = question_text.lower()
        for pattern, reason in VAGUE_PATTERNS:
            if re.search(pattern, lower_text):
                score -= 25.0
                flags.append(f"Vague Phrasing: {reason}")
                suggestions.append("Anchor the question around a concrete technical problem or production invariant.")

        # Check for strong evaluation cues
        has_cue = any(cue in lower_text for cue in STRONG_EVALUATION_CUES)
        if not has_cue and word_count >= 12:
            score -= 10.0
            flags.append("Lacks explicit inquiry into trade-offs, invariants, or edge-case mechanics.")
            suggestions.append("Prompt the candidate to justify trade-offs or handle edge conditions.")

        # Punctuation check
        if not question_text.strip().endswith(("?", ".", "!")):
            score -= 5.0
            flags.append("Missing terminal question mark or punctuation.")

        final_score = max(0.0, min(100.0, score))
        return round(final_score, 1), flags, suggestions
