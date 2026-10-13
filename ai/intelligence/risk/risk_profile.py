from dataclasses import dataclass, field
from typing import Any

from ai.intelligence.risk.finding import (
    RiskFinding,
)
from ai.intelligence.risk.risk_score import (
    calculate_risk_score,
    calculate_severity_counts,
    risk_level,
)


@dataclass
class RiskProfile:

    overall_score: int = 0
    overall_level: str = "INFO"

    security_score: int = 0
    dependency_score: int = 0
    code_score: int = 0
    repository_score: int = 0

    severity_counts: dict[str, int] = field(
        default_factory=dict
    )

    finding_count: int = 0

    affected_files: int = 0

    affected_dependencies: int = 0

    top_risks: list[dict[str, Any]] = field(
        default_factory=list
    )

    risk_drivers: list[str] = field(
        default_factory=list
    )

    findings: list[RiskFinding] = field(
        default_factory=list
    )

    def to_dict(self):

        return {
            "overall_score": self.overall_score,
            "overall_level": self.overall_level,

            "security_score": self.security_score,
            "dependency_score": self.dependency_score,
            "code_score": self.code_score,
            "repository_score": self.repository_score,

            "severity_counts": self.severity_counts,

            "finding_count": self.finding_count,

            "affected_files": self.affected_files,

            "affected_dependencies": (
                self.affected_dependencies
            ),

            "top_risks": self.top_risks,

            "risk_drivers": self.risk_drivers,

            "findings": [
                finding.to_dict()
                for finding in self.findings
            ],
        }