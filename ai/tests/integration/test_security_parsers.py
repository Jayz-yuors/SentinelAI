from ai.integrations.security.parsers import (
    GitleaksParser,
    TrivyParser,
    SemgrepParser,
    DependencyCheckParser,
    SonarParser,
)


def test_gitleaks():
    raw = """
    [
        {
            "RuleID": "generic-api-key",
            "Description": "Generic API Key",
            "File": "config.py",
            "StartLine": 12,
            "Severity": "high"
        }
    ]
    """

    findings = GitleaksParser().parse(raw)

    assert len(findings) == 1
    assert findings[0].source == "gitleaks"
    assert findings[0].rule_id == "generic-api-key"
    assert findings[0].severity == "high"
    assert findings[0].file_path == "config.py"
    assert findings[0].line_number == 12


def test_trivy():
    raw = """
    {
        "Results": [
            {
                "Target": "requirements.txt",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": "CVE-2026-1234",
                        "PkgName": "requests",
                        "InstalledVersion": "1.0",
                        "FixedVersion": "2.0",
                        "Severity": "HIGH",
                        "Title": "Test vulnerability"
                    }
                ]
            }
        ]
    }
    """

    findings = TrivyParser().parse(raw)

    assert len(findings) == 1
    assert findings[0].source == "trivy"
    assert findings[0].rule_id == "CVE-2026-1234"
    assert findings[0].severity == "high"
    assert findings[0].dependency == "requests"


def test_semgrep():
    raw = """
    {
        "results": [
            {
                "check_id": "python.lang.security",
                "path": "app.py",
                "start": {
                    "line": 25
                },
                "extra": {
                    "message": "Unsafe operation",
                    "metadata": {
                        "severity": "ERROR"
                    }
                }
            }
        ]
    }
    """

    findings = SemgrepParser().parse(raw)

    assert len(findings) == 1
    assert findings[0].source == "semgrep"
    assert findings[0].rule_id == "python.lang.security"
    assert findings[0].severity == "high"
    assert findings[0].line_number == 25


def test_dependency_check():
    raw = """
    {
        "dependencies": [
            {
                "fileName": "requests-1.0.jar",
                "vulnerabilities": [
                    {
                        "name": "CVE-2026-5678",
                        "severity": "HIGH",
                        "description": "Test dependency vulnerability"
                    }
                ]
            }
        ]
    }
    """

    findings = DependencyCheckParser().parse(raw)

    assert len(findings) == 1
    assert findings[0].source == "dependency-check"
    assert findings[0].rule_id == "CVE-2026-5678"
    assert findings[0].severity == "high"


def test_sonar():
    raw = """
    {
        "issues": [
            {
                "key": "issue-1",
                "rule": "java:S1234",
                "severity": "CRITICAL",
                "message": "Security issue",
                "component": "src/Main.java",
                "line": 42
            }
        ]
    }
    """

    findings = SonarParser().parse(raw)

    assert len(findings) == 1
    assert findings[0].source == "sonar"
    assert findings[0].rule_id == "java:S1234"
    assert findings[0].severity == "critical"
    assert findings[0].line_number == 42


def run_test():
    print()
    print("=" * 70)
    print(" SENTINELAI — SECURITY PARSER TEST")
    print("=" * 70)

    test_gitleaks()
    print("[PASS] Gitleaks parser")

    test_trivy()
    print("[PASS] Trivy parser")

    test_semgrep()
    print("[PASS] Semgrep parser")

    test_dependency_check()
    print("[PASS] Dependency-Check parser")

    test_sonar()
    print("[PASS] Sonar parser")

    print()
    print("=" * 70)
    print(" SECURITY PARSER TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()