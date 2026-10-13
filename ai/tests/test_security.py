import tempfile

from pathlib import Path

from ai.security.secrets.secret_scanner import (
    analyze_secrets
)

from ai.security.vulnerabilities.vulnerability_scanner import (
    scan_dependencies
)

from ai.security.vulnerabilities.cve_analyzer import (
    analyze_cve_findings
)

from ai.security.static_analysis.security_analyzer import (
    analyze_security
)

from ai.security.threat.threat_analyzer import (
    analyze_threat
)


def create_test_repository():

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    # ------------------------------------------------------------
    # Secret
    # ------------------------------------------------------------

    (
        repository / "config.py"
    ).write_text(
        '''
API_KEY = "12345678901234567890"
password = "supersecret123"
''',
        encoding="utf-8"
    )

    # ------------------------------------------------------------
    # Vulnerable dependency
    # ------------------------------------------------------------

    (
        repository / "requirements.txt"
    ).write_text(
        """
requests==1.0.0
flask==1.0.0
""",
        encoding="utf-8"
    )

    # ------------------------------------------------------------
    # Static security issue
    # ------------------------------------------------------------

    (
        repository / "unsafe.py"
    ).write_text(
        """
user_input = input("Enter code: ")
result = eval(user_input)
""",
        encoding="utf-8"
    )

    return temporary_directory, repository


def run_tests():

    print("=" * 70)
    print("PHASE 2 — SECURITY ANALYSIS TEST")
    print("=" * 70)

    temporary_directory, repository = (
        create_test_repository()
    )

    try:

        # ========================================================
        # SECRET SCANNER
        # ========================================================

        secret_result = analyze_secrets(
            repository
        )

        assert (
            secret_result["totalFindings"] > 0
        )

        print(
            "[PASS] Secret detection"
        )

        # ========================================================
        # VULNERABILITY SCANNER
        # ========================================================

        vulnerability_result = (
            scan_dependencies(
                repository
            )
        )

        assert (
            vulnerability_result[
                "totalDependencies"
            ] > 0
        )

        print(
            "[PASS] Dependency vulnerability scanning"
        )

        # ========================================================
        # CVE ANALYSIS
        # ========================================================

        cve_result = analyze_cve_findings(
            vulnerability_result
        )

        assert "overallRisk" in cve_result

        assert "totalRiskScore" in cve_result

        print(
            "[PASS] CVE risk analysis"
        )

        # ========================================================
        # STATIC ANALYSIS
        # ========================================================

        static_result = analyze_security(
            repository
        )

        assert (
            static_result["totalFindings"] > 0
        )

        print(
            "[PASS] Static security analysis"
        )

        # ========================================================
        # THREAT ANALYSIS
        # ========================================================

        threat_result = analyze_threat(
            secret_result,
            cve_result,
            static_result
        )

        assert "threatScore" in threat_result

        assert "threatLevel" in threat_result

        print(
            "[PASS] Threat analysis"
        )

        print()
        print(
            "Security Findings:",
            threat_result[
                "totalSecurityFindings"
            ]
        )

        print(
            "Threat Level:",
            threat_result[
                "threatLevel"
            ]
        )

        print(
            "Threat Score:",
            threat_result[
                "threatScore"
            ]
        )

        print()
        print("=" * 70)
        print(
            "ALL SECURITY TESTS PASSED"
        )
        print("=" * 70)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_tests()