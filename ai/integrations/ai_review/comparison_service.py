from dataclasses import dataclass
from typing import Any


@dataclass
class RiskComparison:
    """
    Result of comparing security risk before and after
    remediation.
    """

    before_score: int
    after_score: int

    before_level: str
    after_level: str

    score_delta: int
    improved: bool

    @property
    def risk_reduced(self) -> bool:
        return self.improved

    def to_dict(self) -> dict[str, Any]:
        return {
            "before_score": self.before_score,
            "after_score": self.after_score,
            "before_level": self.before_level,
            "after_level": self.after_level,
            "score_delta": self.score_delta,
            "improved": self.improved,
            "risk_reduced": self.risk_reduced,
        }


class RiskComparisonService:
    """
    Canonical service for comparing risk profiles.
    """

    @staticmethod
    def _value(
        profile: Any,
        name: str,
        default: Any = None,
    ):

        if isinstance(profile, dict):
            return profile.get(
                name,
                default,
            )

        return getattr(
            profile,
            name,
            default,
        )

    def compare(
        self,
        before: Any,
        after: Any,
    ) -> RiskComparison:

        before_score = int(
            self._value(
                before,
                "overall_score",
                0,
            )
        )

        after_score = int(
            self._value(
                after,
                "overall_score",
                0,
            )
        )

        before_level = str(
            self._value(
                before,
                "overall_level",
                "INFO",
            )
        )

        after_level = str(
            self._value(
                after,
                "overall_level",
                "INFO",
            )
        )

        return RiskComparison(
            before_score=before_score,
            after_score=after_score,
            before_level=before_level,
            after_level=after_level,
            score_delta=after_score - before_score,
            improved=after_score < before_score,
        )

    def compare_risk(
        self,
        before: Any,
        after: Any,
    ) -> RiskComparison:
        """
        Backward-compatible method name.
        """

        return self.compare(
            before,
            after,
        )


# ---------------------------------------------------------
# Backward-compatible alias
# ---------------------------------------------------------

ComparisonService = RiskComparisonService