from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class PipelineResult:

    success: bool

    analysis_id: str

    status: str

    result: Dict[str, Any] = field(
        default_factory=dict
    )

    error: Optional[str] = None

    attempts: int = 1

    duration_seconds: float = 0.0

    def to_dict(self):

        return {
            "success": self.success,
            "analysisId": self.analysis_id,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "attempts": self.attempts,
            "durationSeconds": (
                self.duration_seconds
            ),
        }