from typing import List, Dict, Any, Optional


class DifficultyCalibrator:
    """
    Dynamically adjusts question difficulty based on candidate seniority and multi-turn performance history.
    """

    DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

    @classmethod
    def calibrate_difficulty(
        cls,
        base_difficulty: str,
        experience_level: str,
        turn_scores: List[float]
    ) -> str:
        """
        Calculates optimal difficulty for the upcoming question turn.
        """
        # Seniority baseline
        level_map = {
            "Junior": "Easy",
            "Mid": "Medium",
            "Senior": "Hard" if base_difficulty == "Hard" else "Medium",
            "Lead": "Hard",
            "Principal": "Hard"
        }
        baseline = level_map.get(experience_level, base_difficulty)

        if not turn_scores:
            return baseline

        recent_avg = sum(turn_scores) / len(turn_scores)
        last_score = turn_scores[-1]

        # Escalation rule
        if recent_avg >= 85.0 and last_score >= 82.0:
            return "Hard"
        
        # De-escalation / calibration rule
        if last_score < 60.0:
            return "Medium" if baseline == "Hard" else "Easy"

        return baseline
