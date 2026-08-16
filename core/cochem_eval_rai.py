"""
CoChem-EVAL: Research Aptitude Index (RAI) Scorer (Suggestion 35)
Implements Socratic logarithmic hint penalty scoring for student evaluation.
"""

import math
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class RAIResult(BaseModel):
    student_id: str
    base_score: float
    hint_count: int
    hint_penalty: float
    rai_score: float
    ast_nodes: int
    commit_count: int
    aptitude_tier: str

class RAIScorer:
    """
    Calculates Research Aptitude Index (RAI) incorporating logarithmic hint penalties:
        Score = Score_base - k * ln(1 + N_hints)
    """
    def __init__(self, default_k: float = 5.0, max_score: float = 100.0) -> None:
        self.default_k = default_k
        self.max_score = max_score

    def calculate_rai(self, base_score: float, hint_count: int, k: float = None) -> float:
        """
        Calculates RAI score applying logarithmic penalty for Socratic hints requested.
        """
        penalty_k = k if k is not None else self.default_k
        hints = max(0, hint_count)
        penalty = penalty_k * math.log(1.0 + hints)
        final_score = max(0.0, min(self.max_score, base_score - penalty))
        return round(final_score, 2)

    def evaluate_student_rai(
        self,
        student_id: str,
        base_score: float,
        hint_count: int,
        ast_nodes: int = 0,
        commit_count: int = 0
    ) -> RAIResult:
        """
        Generates full RAI evaluation model including sub-metrics.
        """
        rai_score = self.calculate_rai(base_score, hint_count)
        hint_penalty = round(base_score - rai_score, 2)

        return RAIResult(
            student_id=student_id,
            base_score=base_score,
            hint_count=hint_count,
            hint_penalty=hint_penalty,
            rai_score=rai_score,
            ast_nodes=ast_nodes,
            commit_count=commit_count,
            aptitude_tier="EXCELLENT" if rai_score >= 90 else ("PROFICIENT" if rai_score >= 75 else "DEVELOPING")
        )