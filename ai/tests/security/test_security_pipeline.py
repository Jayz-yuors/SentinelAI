import tempfile

from pathlib import Path

from ai.security.security_pipeline import (
    analyze_security_pipeline
)


def create_test_repository():

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    (
        repository / "app.py"
    ).write_text(
        """
import os

API_KEY = "12345678901234567890"

value = input("Enter value: ")

result = eval(value)
""",
        encoding="utf-8"
    )

    (
        repository / "requirements.txt"
    ).write_text(
        """
requests==1.0.0
flask==1.0.0
""",
        encoding="utf-8"
    )

    return temporary_directory, repository


def run_tests():

    print("=" * 75)
    print("SENTINELAI — PHASE 2 SECURITY PIPELINE TEST")
    print("=" * 75)

    temporary_directory, repository = (
        create_test_repository()
    )

    try:

        result = analyze_security_pipeline(
            repository
        )

        assert result["success"] is True

        print(
            "[PASS] Security pipeline execution"
        )

        assert (
            "secretAnalysis"
            in result
        )

        print(
            "[PASS] Secret analysis integrated"
        )

        assert (
            "vulnerabilityAnalysis"
            in result
        )

        print(
            "[PASS] Vulnerability analysis integrated"
        )

        assert (
            "cveAnalysis"
            in result
        )

        print(
            "[PASS] CVE analysis integrated"
        )

        assert (
            "staticAnalysis"
            in result
        )

        print(
            "[PASS] Static analysis integrated"
        )

        assert (
            "threatAnalysis"
            in result
        )

        print(
            "[PASS] Threat analysis integrated"
        )

        assert (
            "securityTools"
            in result
        )

        print(
            "[PASS] Security tool integration layer"
        )

        threat = result[
            "threatAnalysis"
        ]

        assert (
            threat["totalSecurityFindings"] > 0
        )

        print(
            "[PASS] Security findings aggregation"
        )

        assert (
            threat["threatScore"] > 0
        )

        print(
            "[PASS] Threat score calculation"
        )

        print()
        print(
            "TOTAL SECURITY FINDINGS:",
            threat[
                "totalSecurityFindings"
            ]
        )

        print(
            "THREAT LEVEL:",
            threat[
                "threatLevel"
            ]
        )

        print(
            "THREAT SCORE:",
            threat[
                "threatScore"
            ]
        )

        print()
        print("=" * 75)
        print(
            "PHASE 2 SECURITY PIPELINE SUCCESSFUL"
        )
        print("=" * 75)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_tests()