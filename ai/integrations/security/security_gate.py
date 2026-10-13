import os
from dataclasses import dataclass

from dotenv import load_dotenv

from ai.intelligence.risk.risk_profile import RiskProfile

load_dotenv()


@dataclass
class SecurityGateResult:

    allowed: bool
    score: int
    threshold: int
    level: str
    critical_count: int
    high_count: int
    reason: str

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "score": self.score,
            "threshold": self.threshold,
            "level": self.level,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "reason": self.reason,
        }


class SecurityGate:

    def __init__(
        self,
        max_score: int | None = None,
        block_critical: bool | None = None,
        block_high: bool | None = None,
    ):

        self.max_score = (
            max_score
            if max_score is not None
            else int(
                os.getenv(
                    "SENTINELAI_SECURITY_GATE_MAX_SCORE",
                    "50",
                )
            )
        )

        self.block_critical = (
            block_critical
            if block_critical is not None
            else os.getenv(
                "SENTINELAI_SECURITY_GATE_BLOCK_CRITICAL",
                "true",
            ).lower() == "true"
        )

        self.block_high = (
            block_high
            if block_high is not None
            else os.getenv(
                "SENTINELAI_SECURITY_GATE_BLOCK_HIGH",
                "false",
            ).lower() == "true"
        )

    def evaluate(
        self,
        profile: RiskProfile,
    ) -> SecurityGateResult:

        counts = profile.severity_counts

        critical_count = counts.get(
            "critical",
            0,
        )

        high_count = counts.get(
            "high",
            0,
        )

        reasons = []

        if profile.overall_score > self.max_score:
            reasons.append(
                f"risk score {profile.overall_score} "
                f"exceeds threshold {self.max_score}"
            )

        if (
            self.block_critical
            and critical_count > 0
        ):
            reasons.append(
                f"{critical_count} critical finding(s)"
            )

        if (
            self.block_high
            and high_count > 0
        ):
            reasons.append(
                f"{high_count} high finding(s)"
            )

        allowed = not reasons

        reason = (
            "Security gate passed."
            if allowed
            else "; ".join(reasons)
        )

        return SecurityGateResult(
            allowed=allowed,
            score=profile.overall_score,
            threshold=self.max_score,
            level=profile.overall_level,
            critical_count=critical_count,
            high_count=high_count,
            reason=reason,
        )