"""
CoChem-EVAL: PI Recruitment Scout & Research Potential Index (RPI) Engine (Suggestion 37)
Ranks students by AST error recovery speed, 3D interaction telemetry, and systematic problem solving
for undergraduate research recruiting draft boards.
"""

from typing import Dict, Any, List
import pandas as pd

class PIRecruitmentScout:
    """
    Evaluates students across problem-solving telemetry metrics to compute a Research Potential Index (RPI)
    and generate a PI Draft Board table for undergraduate research recruitment.
    """
    def __init__(self, w_recovery: float = 0.30, w_telemetry: float = 0.30, w_persistence: float = 0.40):
        self.w_recovery = w_recovery
        self.w_telemetry = w_telemetry
        self.w_persistence = w_persistence

    def calculate_rpi(self, error_recovery_s: float, webgl_rotations: int, clean_attempts: int) -> float:
        """
        Calculates 0-100 RPI score:
        - Recovery score: faster recovery from syntax/logic errors yields higher score (scaled up to 300s).
        - Telemetry score: 3D WebGL rotation interactions show engagement (scaled up to 50 rotations).
        - Persistence score: ratio of clean attempts.
        """
        recovery_score = max(0.0, min(1.0, 1.0 - (error_recovery_s / 300.0)))
        telemetry_score = max(0.0, min(1.0, webgl_rotations / 50.0))
        persistence_score = max(0.0, min(1.0, clean_attempts / 10.0))

        composite = (
            recovery_score * self.w_recovery +
            telemetry_score * self.w_telemetry +
            persistence_score * self.w_persistence
        ) * 100.0

        return round(composite, 2)

    def generate_draft_board(self, student_telemetry_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Generates ranked PI Draft Board dataframe from student telemetry records.
        """
        rows = []
        for record in student_telemetry_list:
            sid = record.get("student_id", "Unknown")
            sname = record.get("student_name", sid)
            rec_s = record.get("error_recovery_s", 60.0)
            rotations = record.get("webgl_rotations", 10)
            attempts = record.get("clean_attempts", 5)

            rpi_score = self.calculate_rpi(rec_s, rotations, attempts)

            tier = "Tier 1 (High Research Aptitude)" if rpi_score >= 80 else (
                "Tier 2 (Promising)" if rpi_score >= 60 else "Tier 3 (Developing)"
            )

            rows.append({
                "Rank": 0,  # Will sort and set rank
                "Student": sname,
                "ID": sid,
                "RPI_Score": rpi_score,
                "Error_Recovery_s": rec_s,
                "3D_Rotations": rotations,
                "Clean_Attempts": attempts,
                "Recruitment_Tier": tier
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values(by="RPI_Score", ascending=False).reset_index(drop=True)
            df["Rank"] = df.index + 1

        return df
