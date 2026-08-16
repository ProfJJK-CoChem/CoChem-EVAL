"""
CoChem-EVAL: 3D WebGL & Interaction Telemetry Collector (Suggestion 38)
Collects 3D viewer rotation events, hint requests, error recovery times, and UI interaction telemetry.
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Union, Optional
from pydantic import BaseModel, Field

class TelemetryEvent(BaseModel):
    type: str
    timestamp: float
    degrees: Optional[float] = None
    hint_level: Optional[int] = None
    duration_s: Optional[float] = None

class TelemetrySummary(BaseModel):
    student_id: str
    webgl_rotations: int
    hint_requests: int
    total_error_recovery_s: float
    event_count: int

class EvalTelemetryCollector:
    """
    Logs student interactive telemetry (3D model rotations, hint requests, error recovery times).
    """
    def __init__(self, student_id: str = "Student_001") -> None:
        self.student_id = student_id
        self.events: List[TelemetryEvent] = []
        self.error_start_time: float = 0.0
        self.total_rotations: int = 0
        self.hint_requests: int = 0

    def log_rotation(self, degrees: float = 15.0) -> Any:
        """Logs a 3D WebGL viewer rotation event."""
        self.total_rotations += 1
        self.events.append(TelemetryEvent(
            type="3D_ROTATION",
            timestamp=time.time(),
            degrees=degrees
        ))

    def log_hint_request(self, hint_level: int = 1) -> Any:
        """Logs a Socratic hint request event."""
        self.hint_requests += 1
        self.events.append(TelemetryEvent(
            type="HINT_REQUEST",
            timestamp=time.time(),
            hint_level=hint_level
        ))

    def log_syntax_error(self) -> Any:
        """Logs syntax error trigger time."""
        self.error_start_time = time.time()
        self.events.append(TelemetryEvent(type="SYNTAX_ERROR_TRIGGERED", timestamp=self.error_start_time))

    def log_syntax_resolution(self) -> float:
        """Logs syntax error resolution time and computes recovery duration in seconds."""
        end_time = time.time()
        duration = round(end_time - self.error_start_time, 2) if self.error_start_time > 0 else 0.0
        self.events.append(TelemetryEvent(
            type="SYNTAX_ERROR_RESOLVED",
            timestamp=end_time,
            duration_s=duration
        ))
        self.error_start_time = 0.0
        return duration

    def get_summary(self) -> TelemetrySummary:
        """Returns consolidated telemetry summary for student."""
        total_recovery = sum(e.duration_s for e in self.events if e.type == "SYNTAX_ERROR_RESOLVED" and e.duration_s is not None)
        return TelemetrySummary(
            student_id=self.student_id,
            webgl_rotations=self.total_rotations,
            hint_requests=self.hint_requests,
            total_error_recovery_s=round(total_recovery, 2),
            event_count=len(self.events)
        )