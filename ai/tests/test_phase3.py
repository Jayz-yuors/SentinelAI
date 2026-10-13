import tempfile

from pathlib import Path

from ai.security.security_pipeline import (
    analyze_security_repository
)


def create_test_repository():

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    (
        repository
        / "config.py"
    ).write_text(
        """
API_KEY = "ABCDEF12345678901234"
PASSWORD = "supersecret123"
""",
        encoding="utf-8"
    )

    (
        repository
        / "app.py"
    ).write_text(
        """
user_input = input("Enter:")
result = eval(user_input)
""",
        encoding="utf-8"
    )

    (
        repository
        / "requirements.txt"
    ).write_text(
        """
requests==2.31.0
""",
        encoding="utf-8"
    )

    return (
        temporary_directory,
        repository
    )


def run_tests():

    print()
    print("=" * 75)
    print("SENTINELAI — PHASE 3 VALIDATION")
    print("=" * 75)

    temporary_directory, repository = (
        create_test_repository()
    )

    try:

        result = (
            analyze_security_repository(
                repository
            )
        )

        # ====================================================
        # TC01 — Pipeline
        # ====================================================

        assert result[
            "success"
        ] is True

        print(
            "[PASS] TC01 — Security pipeline execution"
        )

        analysis = result[
            "securityAnalysis"
        ]

        # ====================================================
        # TC02 — Secrets
        # ====================================================

        assert (
            analysis[
                "secrets"
            ]["totalFindings"]
            >= 2
        )

        print(
            "[PASS] TC02 — Secret detection"
        )

        # ====================================================
        # TC03 — Dependencies
        # ====================================================

        assert len(
            analysis[
                "dependencyVulnerabilities"
            ]["pythonDependencies"]
        ) >= 1

        print(
            "[PASS] TC03 — Dependency extraction"
        )

        # ====================================================
        # TC04 — Static analysis
        # ====================================================

        assert (
            analysis[
                "staticAnalysis"
            ]["totalFindings"]
            >= 1
        )

        print(
            "[PASS] TC04 — Static security analysis"
        )

        # ====================================================
        # TC05 — Threat analysis
        # ====================================================

        assert (
            analysis[
                "threatAnalysis"
            ]["totalThreats"]
            > 0
        )

        print(
            "[PASS] TC05 — Threat classification"
        )

        # ====================================================
        # TC06 — Risk analysis
        # ====================================================

        risk = analysis[
            "risk"
        ]

        assert (
            "overallScore"
            in risk
        )

        assert (
            "overallRisk"
            in risk
        )

        assert (
            "fileRisks"
            in risk
        )

        print(
            "[PASS] TC06 — Security risk scoring"
        )

        # ====================================================
        # TC07 — Final findings
        # ====================================================

        assert len(
            analysis["findings"]
        ) > 0

        print(
            "[PASS] TC07 — Unified security findings"
        )

        print()
        print("-" * 75)

        print(
            "TOTAL FINDINGS:",
            len(
                analysis["findings"]
            )
        )

        print(
            "OVERALL RISK:",
            risk["overallRisk"]
        )

        print(
            "RISK SCORE:",
            risk["overallScore"]
        )

        print("-" * 75)

        print()
        print(
            "PHASE 3 VALIDATION SUCCESSFUL"
        )

        print(
            "ALL TEST CASES PASSED"
        )

        print("=" * 75)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_tests()