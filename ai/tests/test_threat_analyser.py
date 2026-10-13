from ai.security.threat.threat_analyzer import (
    analyze_threats
)


def run_test():

    print("=" * 70)
    print("PHASE 3 — THREAT ANALYZER TEST")
    print("=" * 70)

    findings = [

        {
            "type": "SECRET",
            "category": "API_KEY",
            "file": "config.py",
            "line": 10,
            "severity": "HIGH",
            "message": "API key detected"
        },

        {
            "type": "STATIC_ANALYSIS",
            "category": "DANGEROUS_FUNCTION",
            "file": "app.py",
            "line": 20,
            "severity": "HIGH",
            "message": "eval detected"
        }
    ]

    result = analyze_threats(
        findings
    )

    assert result[
        "totalThreats"
    ] == 2

    assert result[
        "exploitableThreats"
    ] == 2

    assert result[
        "severityCounts"
    ]["HIGH"] == 2

    print(
        "[PASS] Threat classification"
    )

    print(
        "[PASS] Severity calculation"
    )

    print(
        "[PASS] Exploitability analysis"
    )

    print("=" * 70)
    print("THREAT ANALYZER TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()