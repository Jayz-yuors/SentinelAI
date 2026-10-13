from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RiskFinding:

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    source: str
    tool: str

    category: str
    severity: str

    message: str

    # ---------------------------------------------------------
    # Location
    # ---------------------------------------------------------

    file_path: Optional[str] = None
    line_number: Optional[int] = None

    rule_id: Optional[str] = None
    cve_id: Optional[str] = None

    dependency: Optional[str] = None

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------

    evidence: Optional[str] = None

    confidence: float = 1.0

    # ---------------------------------------------------------
    # Correlation
    # ---------------------------------------------------------

    fingerprint: Optional[str] = None

    related_findings: list[str] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Additional metadata
    # ---------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:

        return {
            "source": self.source,
            "tool": self.tool,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "rule_id": self.rule_id,
            "cve_id": self.cve_id,
            "dependency": self.dependency,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "fingerprint": self.fingerprint,
            "related_findings": self.related_findings,
            "metadata": self.metadata,
        }