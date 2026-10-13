import json

from ai.intelligence.risk.risk_engine import (
    UnifiedRiskEngine,
)


def main():

    print()
    print("=" * 75)
    print(
        " SENTINELAI — UNIFIED RISK INTELLIGENCE TEST"
    )
    print("=" * 75)
    print()

    findings = [

        # -----------------------------------------------------
        # Secret
        # -----------------------------------------------------

        {
            "source": "sentinelai",
            "tool": "secret-scanner",
            "category": "secret",
            "severity": "high",
            "message": "Hardcoded API key detected",
            "file_path": "src/config.py",
            "line_number": 21,
            "rule_id": "API_KEY",
            "evidence": "API_KEY=...",
            "confidence": 0.98,
        },

        # Duplicate
        {
            "source": "gitleaks",
            "tool": "gitleaks",
            "category": "secret",
            "severity": "high",
            "message": "Hardcoded API key detected",
            "file_path": "src/config.py",
            "line_number": 21,
            "rule_id": "API_KEY",
            "confidence": 0.95,
        },

        # -----------------------------------------------------
        # Dependency
        # -----------------------------------------------------

        {
            "source": "trivy",
            "tool": "trivy",
            "category": "dependency",
            "severity": "critical",
            "message": "Vulnerable dependency detected",
            "file_path": "requirements.txt",
            "line_number": 4,
            "dependency": "example-package",
            "cve_id": "CVE-TEST-0001",
            "confidence": 1.0,
        },

        # -----------------------------------------------------
        # Code
        # -----------------------------------------------------

        {
            "source": "semgrep",
            "tool": "semgrep",
            "category": "static_analysis",
            "severity": "medium",
            "message": "Unsafe subprocess usage",
            "file_path": "src/runner.py",
            "line_number": 55,
            "rule_id": "python.security",
            "confidence": 0.90,
        },

        # -----------------------------------------------------
        # Dependency
        # -----------------------------------------------------

        {
            "source": "dependency-check",
            "tool": "owasp-dependency-check",
            "category": "dependency",
            "severity": "high",
            "message": "Known vulnerable package",
            "file_path": "pom.xml",
            "line_number": 88,
            "dependency": "example-java-package",
            "cve_id": "CVE-TEST-0002",
            "confidence": 1.0,
        },
    ]

    # ---------------------------------------------------------
    # 1. Engine initialization
    # ---------------------------------------------------------

    print("[1] Initializing risk engine...")

    engine = UnifiedRiskEngine()

    print(
        "[PASS] Risk engine initialized"
    )

    print()

    # ---------------------------------------------------------
    # 2. Analysis
    # ---------------------------------------------------------

    print(
        "[2] Running unified risk analysis..."
    )

    profile = engine.analyze(
        findings
    )

    print(
        "[PASS] Unified analysis completed"
    )

    print()

    # ---------------------------------------------------------
    # 3. Finding count
    # ---------------------------------------------------------

    print(
        "[3] Validating finding normalization..."
    )

    assert profile.finding_count == 4

    print(
        f"[PASS] Unique findings = "
        f"{profile.finding_count}"
    )

    print()

    # ---------------------------------------------------------
    # 4. Severity
    # ---------------------------------------------------------

    print(
        "[4] Validating severity counts..."
    )

    counts = (
        profile.severity_counts
    )

    assert counts["critical"] == 1
    assert counts["high"] == 2
    assert counts["medium"] == 1

    print(
        "[PASS] Severity distribution"
    )

    print()

    # ---------------------------------------------------------
    # 5. Risk score
    # ---------------------------------------------------------

    print(
        "[5] Validating risk score..."
    )

    assert (
        0
        <= profile.overall_score
        <= 100
    )

    print(
        f"[PASS] Overall score = "
        f"{profile.overall_score}"
    )

    print(
        f"[INFO] Overall level = "
        f"{profile.overall_level}"
    )

    print()

    # ---------------------------------------------------------
    # 6. Category scores
    # ---------------------------------------------------------

    print(
        "[6] Validating category risk..."
    )

    assert profile.security_score >= 0
    assert profile.dependency_score >= 0
    assert profile.code_score >= 0

    print(
        f"[PASS] Security score = "
        f"{profile.security_score}"
    )

    print(
        f"[PASS] Dependency score = "
        f"{profile.dependency_score}"
    )

    print(
        f"[PASS] Code score = "
        f"{profile.code_score}"
    )

    print()

    # ---------------------------------------------------------
    # 7. Affected assets
    # ---------------------------------------------------------

    print(
        "[7] Validating affected assets..."
    )

    assert profile.affected_files == 4
    assert profile.affected_dependencies == 2

    print(
        f"[PASS] Affected files = "
        f"{profile.affected_files}"
    )

    print(
        f"[PASS] Affected dependencies = "
        f"{profile.affected_dependencies}"
    )

    print()

    # ---------------------------------------------------------
    # 8. Top risks
    # ---------------------------------------------------------

    print(
        "[8] Validating top risks..."
    )

    assert profile.top_risks

    print(
        f"[PASS] Top risks = "
        f"{len(profile.top_risks)}"
    )

    print()

    # ---------------------------------------------------------
    # 9. Serialization
    # ---------------------------------------------------------

    print(
        "[9] Validating JSON serialization..."
    )

    data = profile.to_dict()

    serialized = json.dumps(
        data,
        indent=2,
    )

    assert serialized

    print(
        "[PASS] Risk profile serialized"
    )

    print()

    # ---------------------------------------------------------
    # 10. Display summary
    # ---------------------------------------------------------

    print(
        "[10] Unified risk summary"
    )

    print(
        json.dumps(
            {
                "overall_score":
                    profile.overall_score,

                "overall_level":
                    profile.overall_level,

                "security_score":
                    profile.security_score,

                "dependency_score":
                    profile.dependency_score,

                "code_score":
                    profile.code_score,

                "severity_counts":
                    profile.severity_counts,

                "finding_count":
                    profile.finding_count,

                "affected_files":
                    profile.affected_files,

                "affected_dependencies":
                    profile.affected_dependencies,
            },
            indent=2,
        )
    )

    print()

    # ---------------------------------------------------------
    # Final
    # ---------------------------------------------------------

    print("=" * 75)
    print(
        " UNIFIED RISK INTELLIGENCE TEST PASSED"
    )
    print("=" * 75)
    print()


if __name__ == "__main__":
    main()