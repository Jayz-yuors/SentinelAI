import ast
from pathlib import Path

from .comparison_service import RiskComparisonService
from .review_models import VerificationResult


class AIVerificationService:
    """Verification adapter. Uses security pipeline when supplied, plus syntax validation."""

    def __init__(self, security_pipeline=None):
        self.security_pipeline = security_pipeline
        self.comparison_service = RiskComparisonService()

    def verify(self, repository_path: str, before_profile) -> VerificationResult:
        if self.security_pipeline is None:
            raise ValueError(
                "A security pipeline is required for risk-based verification. "
                "Use verify_code_change for the local integration smoke test."
            )

        result = self.security_pipeline.run_all_available(repository_path)
        comparison = self.comparison_service.compare(
            before_profile,
            result.risk_profile,
        )

        return VerificationResult(
            verified=comparison.improved,
            before_score=comparison.before_score,
            after_score=comparison.after_score,
            before_level=comparison.before_level,
            after_level=comparison.after_level,
            remaining_findings=result.findings,
            resolved_finding_ids=getattr(comparison, "resolved_findings", []),
            new_finding_ids=getattr(comparison, "new_findings", []),
            summary=(
                f"Risk score changed from {comparison.before_score} "
                f"to {comparison.after_score}."
            ),
        )

    def verify_code_change(
        self,
        repository_path: str,
        target: str,
        developer_reason: str,
    ) -> dict:
        path = (Path(repository_path) / target).resolve()
        repository = Path(repository_path).resolve()

        if not str(path).startswith(str(repository)):
            raise ValueError("Verification target escapes repository.")

        if not path.exists():
            return {
                "verified": False,
                "method": "static",
                "reason": "Target file does not exist.",
            }

        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError as exc:
                return {
                    "verified": False,
                    "method": "python_ast",
                    "reason": f"Python syntax error: {exc}",
                }

        return {
            "verified": True,
            "method": "static",
            "reason": "Target file passed available local syntax verification.",
            "developer_reason": developer_reason,
        }
