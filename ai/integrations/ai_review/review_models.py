from dataclasses import dataclass, field
from typing import Any


@dataclass
class CodeReviewFinding:
    finding_id: str
    severity: str
    title: str
    explanation: str
    file_path: str | None = None
    line_number: int | None = None
    recommendation: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CodeReviewResult:
    summary: str
    findings: list[CodeReviewFinding]
    provider: str | None = None
    model: str | None = None
    raw_response: str | None = None


@dataclass
class RemediationProposal:
    finding_id: str
    file_path: str
    explanation: str
    original_code: str
    replacement_code: str
    patch: str
    confidence: float | None = None
    provider: str | None = None
    model: str | None = None


@dataclass
class VerificationResult:
    verified: bool
    before_score: float
    after_score: float
    before_level: str
    after_level: str
    remaining_findings: list[Any] = field(
        default_factory=list
    )
    resolved_finding_ids: list[str] = field(
        default_factory=list
    )
    new_finding_ids: list[str] = field(
        default_factory=list
    )
    summary: str = ""