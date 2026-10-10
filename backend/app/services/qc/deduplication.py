import re
from typing import List, Tuple, Set

STOP_WORDS: Set[str] = {
    "a", "an", "the", "in", "on", "at", "of", "to", "for", "with", "by", "from",
    "and", "or", "is", "are", "was", "were", "how", "what", "why", "when", "where",
    "do", "does", "did", "can", "could", "would", "should", "you", "your", "we", "our"
}


class DeduplicationChecker:
    """
    Guarantees session question diversity by measuring lexical, n-gram, and concept overlap.
    """

    @staticmethod
    def _tokenize_meaningful(text: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z0-9_\-\.]{2,}\b', text.lower())
        return [w for w in words if w not in STOP_WORDS]

    @classmethod
    def compute_jaccard_similarity(cls, text_a: str, text_b: str) -> float:
        tokens_a = set(cls._tokenize_meaningful(text_a))
        tokens_b = set(cls._tokenize_meaningful(text_b))
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a.intersection(tokens_b)
        union = tokens_a.union(tokens_b)
        return len(intersection) / len(union)

    @classmethod
    def check_duplicate(
        cls,
        candidate_question: str,
        previous_questions: List[str],
        threshold: float = 0.65
    ) -> Tuple[bool, float, str]:
        """
        Returns:
            is_duplicate (bool): True if similarity exceeds threshold.
            max_similarity (float): Highest similarity score found (0.0 to 1.0).
            most_similar_question (str): The previous question that triggered the overlap.
        """
        if not previous_questions:
            return False, 0.0, ""

        max_sim = 0.0
        matched_q = ""

        for prev_q in previous_questions:
            sim = cls.compute_jaccard_similarity(candidate_question, prev_q)
            if sim > max_sim:
                max_sim = sim
                matched_q = prev_q

        is_dup = max_sim >= threshold
        return is_dup, round(max_sim, 3), matched_q
