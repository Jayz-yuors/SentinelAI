from ai.intelligence.risk.finding import (
    RiskFinding,
)
from ai.intelligence.risk.fingerprint import (
    generate_fingerprint,
)


def main():

    print()
    print("=" * 65)
    print(
        " SENTINELAI — RISK FINDING TEST"
    )
    print("=" * 65)
    print()

    finding = RiskFinding(

        source="sentinelai",

        tool="secret-scanner",

        category="secret",

        severity="high",

        message="API key detected",

        file_path="src/config.py",

        line_number=42,

        rule_id="API_KEY",

        evidence="API_KEY=abc123",

        confidence=0.95,
    )

    print("[1] Finding creation...")

    assert finding.message == (
        "API key detected"
    )

    print(
        "[PASS] Finding creation"
    )

    print()

    print("[2] Fingerprint generation...")

    fingerprint = (
        generate_fingerprint(
            finding
        )
    )

    assert fingerprint
    assert len(fingerprint) == 64

    finding.fingerprint = fingerprint

    print(
        "[PASS] Fingerprint generation"
    )

    print()

    print("[3] Serialization...")

    data = finding.to_dict()

    assert data["source"] == (
        "sentinelai"
    )

    assert data["severity"] == (
        "high"
    )

    assert data["fingerprint"]

    print(
        "[PASS] Finding serialization"
    )

    print()

    print("=" * 65)
    print(
        " RISK FINDING TEST PASSED"
    )
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()