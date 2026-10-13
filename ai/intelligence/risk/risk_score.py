from collections import Counter

from ai.intelligence.risk.finding import (
    RiskFinding,
)
from ai.intelligence.risk.severity import (
    Severity,
    normalize_severity,
)


SEVERITY_WEIGHTS = {

    Severity.INFO: 0,

    Severity.LOW: 5,

    Severity.MEDIUM: 15,

    Severity.HIGH: 30,

    Severity.CRITICAL: 50,
}


def calculate_risk_score(
    findings: list[RiskFinding],
) -> int:

    if not findings:
        return 0

    raw_score = 0.0

    for finding in findings:

        severity = normalize_severity(
            finding.severity
        )

        weight = SEVERITY_WEIGHTS[
            severity
        ]

        confidence = max(
            0.0,
            min(
                finding.confidence,
                1.0,
            ),
        )

        raw_score += (
            weight
            * confidence
        )

    # Prevent unbounded repository scores.
    return min(
        100,
        round(raw_score),
    )


def calculate_severity_counts(
    findings: list[RiskFinding],
) -> dict[str, int]:

    counts = Counter()

    for finding in findings:

        severity = normalize_severity(
            finding.severity
        )

        counts[
            severity.name.lower()
        ] += 1

    return {
        "info": counts["info"],
        "low": counts["low"],
        "medium": counts["medium"],
        "high": counts["high"],
        "critical": counts["critical"],
    }


def risk_level(
    score: int,
) -> str:

    if score >= 75:
        return "CRITICAL"

    if score >= 50:
        return "HIGH"

    if score >= 25:
        return "MEDIUM"

    if score > 0:
        return "LOW"

    return "INFO"