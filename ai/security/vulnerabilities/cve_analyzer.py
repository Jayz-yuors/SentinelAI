# ============================================================
# CVE SEVERITY MAP
# ============================================================

SEVERITY_SCORES = {

    "CRITICAL": 10,

    "HIGH": 8,

    "MEDIUM": 5,

    "LOW": 2,

    "UNKNOWN": 1
}


# ============================================================
# CVE CLASSIFICATION
# ============================================================

def classify_cve(
    vulnerability: dict
):

    cve_id = vulnerability.get(
        "id"
    )

    description = (
        vulnerability.get(
            "description"
        )
        or ""
    )

    description_lower = (
        description.lower()
    )

    if any(
        word in description_lower
        for word in [
            "remote code execution",
            "arbitrary code execution",
            "command injection"
        ]
    ):

        severity = "CRITICAL"

    elif any(
        word in description_lower
        for word in [
            "sql injection",
            "authentication bypass",
            "privilege escalation"
        ]
    ):

        severity = "HIGH"

    elif any(
        word in description_lower
        for word in [
            "cross-site scripting",
            "xss",
            "denial of service"
        ]
    ):

        severity = "MEDIUM"

    else:

        severity = "UNKNOWN"

    return {

        "id": cve_id,

        "package":
            vulnerability.get(
                "package"
            ),

        "version":
            vulnerability.get(
                "version"
            ),

        "severity":
            severity,

        "severityScore":
            SEVERITY_SCORES[
                severity
            ],

        "description":
            description,

        "fixVersions":
            vulnerability.get(
                "fix_versions",
                []
            )
    }


# ============================================================
# ANALYZE CVEs
# ============================================================

def analyze_cves(
    vulnerabilities: list
):

    analyzed = []

    for vulnerability in vulnerabilities:

        analyzed.append(
            classify_cve(
                vulnerability
            )
        )

    return {

        "totalCVEs":
            len(analyzed),

        "findings":
            analyzed
    }