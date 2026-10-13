from pathlib import Path

from ai.security.secrets.secret_scanner import (
    analyze_secrets
)

from ai.security.vulnerabilities.vulnerability_scanner import (
    scan_dependencies
)

from ai.security.vulnerabilities.cve_analyzer import (
    analyze_cves
)

from ai.security.static_analysis.security_analyzer import (
    analyze_security
)

from ai.security.threat.threat_analyzer import (
    analyze_threats
)

from ai.security.security_risk_model import (
    calculate_security_risk
)


# ============================================================
# SECURITY PIPELINE
# ============================================================

def analyze_security_repository(
    repository_path: Path,
    dependency_analysis=None
):

    repository_path = Path(
        repository_path
    )

    # ========================================================
    # 1. SECRET SCANNING
    # ========================================================

    secret_result = analyze_secrets(
        repository_path
    )

    # ========================================================
    # 2. DEPENDENCY VULNERABILITY SCANNING
    # ========================================================

    dependency_result = scan_dependencies(
        repository_path
    )

    # ========================================================
    # 3. CVE ANALYSIS
    # ========================================================

    cve_result = analyze_cves(
        dependency_result.get(
            "vulnerabilities",
            []
        )
    )

    # ========================================================
    # 4. STATIC SECURITY ANALYSIS
    # ========================================================

    static_result = analyze_security(
        repository_path
    )

    # ========================================================
    # 5. COMBINE SECURITY FINDINGS
    # ========================================================

    all_findings = []

    # --------------------------------------------------------
    # Secret findings
    # --------------------------------------------------------

    all_findings.extend(
        secret_result.get(
            "findings",
            []
        )
    )

    # --------------------------------------------------------
    # Static security findings
    # --------------------------------------------------------

    all_findings.extend(
        static_result.get(
            "findings",
            []
        )
    )

    # --------------------------------------------------------
    # CVE findings
    # --------------------------------------------------------

    for cve in cve_result.get(
        "findings",
        []
    ):

        all_findings.append({

            "type":
                "CVE",

            "category":
                "VULNERABLE_DEPENDENCY",

            "file":
                None,

            "line":
                None,

            "severity":
                cve.get(
                    "severity",
                    "UNKNOWN"
                ),

            "message":
                cve.get(
                    "description",
                    ""
                ),

            "id":
                cve.get(
                    "id"
                ),

            "package":
                cve.get(
                    "package"
                ),

            "version":
                cve.get(
                    "version"
                ),

            "fixVersions":
                cve.get(
                    "fixVersions",
                    []
                )
        })

    # ========================================================
    # 6. THREAT ANALYSIS
    # ========================================================

    threat_result = analyze_threats(
        all_findings
    )

    # ========================================================
    # 7. SECURITY RISK SCORING
    # ========================================================

    risk_result = calculate_security_risk(
        all_findings
    )

    # ========================================================
    # 8. FINAL SECURITY RESULT
    # ========================================================

    result = {

        "success":
            True,

        "securityAnalysis": {

            # ------------------------------------------------
            # Phase 3 components
            # ------------------------------------------------

            "secrets":
                secret_result,

            "dependencyVulnerabilities":
                dependency_result,

            "cves":
                cve_result,

            "staticAnalysis":
                static_result,

            "threatAnalysis":
                threat_result,

            "risk":
                risk_result,

            "findings":
                all_findings,

            # ------------------------------------------------
            # Phase 2 context
            # ------------------------------------------------

            "dependencyContext":
                dependency_analysis
                if dependency_analysis is not None
                else {}
        },

        "message":
            "Security analysis completed successfully"
    }

    return result