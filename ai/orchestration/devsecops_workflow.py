from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from ai.integrations.git.candidate_manager import (
    CandidateBranchManager,
)

from ai.integrations.security.security_gate import (
    SecurityGate,
    SecurityGateResult,
)


@dataclass
class RiskComparison:
    before_score: int
    after_score: int
    score_delta: int
    before_level: str
    after_level: str
    improved: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "before_score": self.before_score,
            "after_score": self.after_score,
            "score_delta": self.score_delta,
            "before_level": self.before_level,
            "after_level": self.after_level,
            "improved": self.improved,
        }


@dataclass
class DevSecOpsWorkflowResult:
    repository_path: str
    candidate_branch: Optional[str] = None

    before_risk: Optional[dict[str, Any]] = None
    after_risk: Optional[dict[str, Any]] = None
    comparison: Optional[RiskComparison] = None

    gate: Optional[SecurityGateResult] = None

    review: Optional[dict[str, Any]] = None
    remediation: Optional[dict[str, Any]] = None
    verification: Optional[dict[str, Any]] = None

    commit_sha: Optional[str] = None
    pushed: bool = False

    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_path": self.repository_path,
            "candidate_branch": self.candidate_branch,
            "before_risk": self.before_risk,
            "after_risk": self.after_risk,
            "comparison": (
                self.comparison.to_dict()
                if self.comparison
                else None
            ),
            "gate": (
                self.gate.to_dict()
                if self.gate
                else None
            ),
            "review": self.review,
            "remediation": self.remediation,
            "verification": self.verification,
            "commit_sha": self.commit_sha,
            "pushed": self.pushed,
            "errors": self.errors,
        }


class DevSecOpsWorkflow:

    def __init__(
        self,
        scanner: Callable[[str], Any],
        review_service: Any | None = None,
        remediation_service: Any | None = None,
        verification_service: Any | None = None,
        comparison_service: Any | None = None,
        candidate_manager: CandidateBranchManager | None = None,
        security_gate: SecurityGate | None = None,
    ):
        self.scanner = scanner

        self.review_service = review_service
        self.remediation_service = remediation_service
        self.verification_service = verification_service
        self.comparison_service = comparison_service

        self.candidate_manager = (
            candidate_manager
            or CandidateBranchManager()
        )

        self.security_gate = (
            security_gate
            or SecurityGate()
        )

    # ---------------------------------------------------------
    # SCAN
    # ---------------------------------------------------------

    def scan(
        self,
        repository_path: str,
    ) -> Any:

        path = Path(repository_path).resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {path}"
            )

        return self.scanner(str(path))

    # ---------------------------------------------------------
    # RISK EXTRACTION
    # ---------------------------------------------------------

    @staticmethod
    def risk_to_dict(profile: Any) -> dict[str, Any]:

        if profile is None:
            return {}

        if isinstance(profile, dict):
            return profile

        if hasattr(profile, "to_dict"):
            return profile.to_dict()

        result = {}

        for field_name in (
            "overall_score",
            "overall_level",
            "security_score",
            "dependency_score",
            "code_score",
            "repository_score",
            "severity_counts",
            "finding_count",
            "affected_files",
            "affected_dependencies",
        ):
            if hasattr(profile, field_name):
                result[field_name] = getattr(
                    profile,
                    field_name,
                )

        return result

    # ---------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------

    def compare_risk(
        self,
        before: Any,
        after: Any,
    ) -> RiskComparison:

        before_dict = self.risk_to_dict(before)
        after_dict = self.risk_to_dict(after)

        before_score = int(
            before_dict.get("overall_score", 0)
        )

        after_score = int(
            after_dict.get("overall_score", 0)
        )

        before_level = str(
            before_dict.get(
                "overall_level",
                "INFO",
            )
        )

        after_level = str(
            after_dict.get(
                "overall_level",
                "INFO",
            )
        )

        return RiskComparison(
            before_score=before_score,
            after_score=after_score,
            score_delta=after_score - before_score,
            before_level=before_level,
            after_level=after_level,
            improved=after_score < before_score,
        )

    # ---------------------------------------------------------
    # CANDIDATE
    # ---------------------------------------------------------

    def create_candidate(
        self,
        repository_path: str,
    ):

        return self.candidate_manager.create_candidate(
            repository_path
        )

    # ---------------------------------------------------------
    # SECURITY GATE
    # ---------------------------------------------------------

    def evaluate_gate(
        self,
        risk_profile: Any,
    ) -> SecurityGateResult:

        return self.security_gate.evaluate(
            risk_profile
        )

    # ---------------------------------------------------------
    # COMPLETE ANALYSIS
    # ---------------------------------------------------------

    def analyze(
        self,
        repository_path: str,
    ) -> DevSecOpsWorkflowResult:

        result = DevSecOpsWorkflowResult(
            repository_path=str(
                Path(repository_path).resolve()
            )
        )

        before_profile = self.scan(
            repository_path
        )

        result.before_risk = self.risk_to_dict(
            before_profile
        )

        return result

    # ---------------------------------------------------------
    # FULL REMEDIATION FLOW
    # ---------------------------------------------------------

    def remediate(
        self,
        repository_path: str,
        auto_commit: bool = False,
        auto_push: bool = False,
    ) -> DevSecOpsWorkflowResult:

        result = self.analyze(
            repository_path
        )

        # ---------------------------------------------
        # AI REVIEW
        # ---------------------------------------------

        if self.review_service is not None:

            review = self.review_service.review(
                result.before_risk
            )

            if hasattr(review, "to_dict"):
                review = review.to_dict()

            result.review = review

        # ---------------------------------------------
        # CREATE CANDIDATE BRANCH
        # ---------------------------------------------

        candidate = self.create_candidate(
            repository_path
        )

        result.candidate_branch = (
            candidate.candidate_branch
        )

        # ---------------------------------------------
        # AI REMEDIATION
        # ---------------------------------------------

        if self.remediation_service is not None:

            remediation = (
                self.remediation_service.remediate(
                    repository_path=repository_path,
                    review=result.review,
                )
            )

            if hasattr(remediation, "to_dict"):
                remediation = remediation.to_dict()

            result.remediation = remediation

        # ---------------------------------------------
        # VERIFICATION
        # ---------------------------------------------

        if self.verification_service is not None:

            verification = (
                self.verification_service.verify(
                    repository_path
                )
            )

            if hasattr(verification, "to_dict"):
                verification = verification.to_dict()

            result.verification = verification

        # ---------------------------------------------
        # RESCAN
        # ---------------------------------------------

        after_profile = self.scan(
            repository_path
        )

        result.after_risk = self.risk_to_dict(
            after_profile
        )

        result.comparison = self.compare_risk(
            before_profile,
            after_profile,
        )

        # ---------------------------------------------
        # SECURITY GATE
        # ---------------------------------------------

        result.gate = self.evaluate_gate(
            after_profile
        )

        # ---------------------------------------------
        # COMMIT
        # ---------------------------------------------

        if (
            auto_commit
            and result.gate.allowed
            and self.candidate_manager.has_changes(
                repository_path
            )
        ):

            result.commit_sha = (
                self.candidate_manager.commit_changes(
                    repository_path,
                    "fix: SentinelAI security remediation",
                )
            )

        # ---------------------------------------------
        # PUSH
        # ---------------------------------------------

        if (
            auto_push
            and result.gate.allowed
            and result.commit_sha
        ):

            self.candidate_manager.push(
                repository_path,
                candidate.candidate_branch,
            )

            result.pushed = True

        return result