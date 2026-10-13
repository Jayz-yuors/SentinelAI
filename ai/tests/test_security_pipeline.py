import tempfile

from pathlib import Path

from ai.security.security_pipeline import (
    analyze_security_repository
)


def create_repository():

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    # Secret
    (
        repository
        / "config.py"
    ).write_text(
        """
API_KEY = "ABCDEF12345678901234"
PASSWORD = "secret123"
""",
        encoding="utf-8"
    )

    # Unsafe code
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

    # Dependency manifest
    (
        repository
        / "requirements.txt"
    ).write_text(
        """
requests==2.31.0
flask==3.0.0
""",
        encoding="utf-8"
    )

    return (
        temporary_directory,
        repository
    )


def run_test():

    print("=" * 70)
    print(
        "PHASE 3 — COMPLETE SECURITY PIPELINE TEST"
    )
    print("=" * 70)

    temporary_directory, repository = (
        create_repository()
    )

    try:

        result = (
            analyze_security_repository(
                repository
            )
        )

        assert result[
            "success"
        ] is True

        print(
            "[PASS] Security pipeline execution"
        )

        analysis = result[
            "securityAnalysis"
        ]

        assert (
            "secrets"
            in analysis
        )

        print(
            "[PASS] Secret analysis"
        )

        assert (
            "dependencyVulnerabilities"
            in analysis
        )

        print(
            "[PASS] Dependency analysis"
        )

        assert (
            "cves"
            in analysis
        )

        print(
            "[PASS] CVE analysis"
        )

        assert (
            "staticAnalysis"
            in analysis
        )

        print(
            "[PASS] Static security analysis"
        )

        assert (
            "threatAnalysis"
            in analysis
        )

        print(
            "[PASS] Threat analysis"
        )

        assert (
            "risk"
            in analysis
        )

        print(
            "[PASS] Security risk scoring"
        )

        findings = analysis[
            "findings"
        ]

        assert len(
            findings
        ) > 0

        print(
            "[PASS] Security findings generated"
        )

        risk = analysis[
            "risk"
        ]

        print()
        print(
            "Total Findings:",
            len(findings)
        )

        print(
            "Overall Risk:",
            risk["overallRisk"]
        )

        print(
            "Risk Score:",
            risk["overallScore"]
        )

        print()
        print("=" * 70)
        print(
            "COMPLETE SECURITY PIPELINE TEST PASSED"
        )
        print("=" * 70)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_test()