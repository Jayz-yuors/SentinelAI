from ai.intelligence.risk.risk_engine import (
    UnifiedRiskEngine,
)


def main():

    print()
    print("=" * 65)
    print(
        " SENTINELAI — RISK CORRELATION TEST"
    )
    print("=" * 65)
    print()

    findings = [

        {
            "source": "sentinelai",
            "tool": "secret-scanner",
            "category": "secret",
            "severity": "high",
            "message": "API key detected",
            "file_path": "app.py",
            "line_number": 10,
            "rule_id": "API_KEY",
        },

        {
            "source": "semgrep",
            "tool": "semgrep",
            "category": "secret",
            "severity": "high",
            "message": "Hardcoded credential",
            "file_path": "app.py",
            "line_number": 10,
            "rule_id": "hardcoded-secret",
        },

        {
            "source": "sentinelai",
            "tool": "secret-scanner",
            "category": "secret",
            "severity": "high",
            "message": "API key detected",
            "file_path": "app.py",
            "line_number": 10,
            "rule_id": "API_KEY",
        },
    ]

    engine = UnifiedRiskEngine()

    print("[1] Running unified analysis...")

    profile = engine.analyze(
        findings
    )

    print(
        "[PASS] Analysis completed"
    )

    print()

    print("[2] Checking deduplication...")

    # Two exact duplicate findings
    # should become one.
    assert profile.finding_count == 2

    print(
        "[PASS] Duplicate finding removed"
    )

    print()

    print("[3] Checking correlation...")

    correlated = [
        finding
        for finding in profile.findings
        if finding.related_findings
    ]

    assert correlated

    print(
        "[PASS] Related findings correlated"
    )

    print()

    print("=" * 65)
    print(
        " RISK CORRELATION TEST PASSED"
    )
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()