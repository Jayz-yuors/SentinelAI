from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class UnifiedAnalysis:

    analysis_id: str

    phase1: Dict[str, Any] = field(
        default_factory=dict
    )

    phase2: Dict[str, Any] = field(
        default_factory=dict
    )

    phase3: Dict[str, Any] = field(
        default_factory=dict
    )

    status: str = "QUEUED"

    def to_dict(self):

        return {
            "analysisId": self.analysis_id,
            "status": self.status,
            "phase1": self.phase1,
            "phase2": self.phase2,
            "phase3": self.phase3,
        }