from ai.intelligence.risk.finding import (
    RiskFinding,
)

from ai.intelligence.risk.risk_score import (
    calculate_risk_score,
    calculate_severity_counts,
    risk_level,
)


def main():

    print()
    print("=" * 65)
    print(
        " SENTINELAI — RISK SCORING TEST"
    )
    print("=" * 65)
    print()

    findings = [

        RiskFinding(
            source="test",
            tool="test",
            category="secret",
            severity="critical",
            message="Critical secret",
            confidence=1.0,
        ),

        RiskFinding(
            source="test",
            tool="test",
            category="vulnerability",
            severity="high",
            message="High vulnerability",
            confidence=1.0,
        ),

        RiskFinding(
            source="test",
            tool="test",
            category="code",
            severity="medium",
            message="Medium issue",
            confidence=1.0,
        ),
    ]

    print("[1] Calculating risk score...")

    score = calculate_risk_score(
        findings
    )

    assert score > 0
    assert score <= 100

    print(
        f"[PASS] Risk score = {score}"
    )

    print()

    print("[2] Severity counts...")

    counts = calculate_severity_counts(
        findings
    )

    assert counts["critical"] == 1
    assert counts["high"] == 1
    assert counts["medium"] == 1

    print(
        "[PASS] Severity counts"
    )

    print()

    print("[3] Risk level...")

    level = risk_level(
        score
    )

    assert level in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    print(
        f"[PASS] Risk level = {level}"
    )

    print()

    print("=" * 65)
    print(
        " RISK SCORING TEST PASSED"
    )
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()