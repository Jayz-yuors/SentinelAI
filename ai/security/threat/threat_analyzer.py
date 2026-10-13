SEVERITY_SCORES = {

    "CRITICAL": 10,

    "HIGH": 8,

    "MEDIUM": 5,

    "LOW": 2,

    "INFO": 0,

    "UNKNOWN": 1
}


# ============================================================
# THREAT CLASSIFICATION
# ============================================================

def classify_threat(
    finding: dict
):

    category = (
        finding.get(
            "category",
            ""
        )
        .upper()
    )

    severity = (
        finding.get(
            "severity",
            "UNKNOWN"
        )
        .upper()
    )

    if category in {
        "API_KEY",
        "PASSWORD",
        "TOKEN",
        "PRIVATE_KEY",
        "AWS_ACCESS_KEY",
        "GITHUB_TOKEN"
    }:

        threat_type = (
            "CREDENTIAL_EXPOSURE"
        )

    elif category in {
        "COMMAND_EXECUTION",
        "DANGEROUS_FUNCTION"
    }:

        threat_type = (
            "CODE_EXECUTION"
        )

    elif (
        finding.get("id")
        and str(
            finding.get("id")
        ).upper().startswith("CVE")
    ):

        threat_type = (
            "VULNERABLE_DEPENDENCY"
        )

    else:

        threat_type = (
            "SECURITY_WEAKNESS"
        )

    return {

        "threatType":
            threat_type,

        "severity":
            severity,

        "severityScore":
            SEVERITY_SCORES.get(
                severity,
                1
            ),

        "file":
            finding.get(
                "file"
            ),

        "line":
            finding.get(
                "line"
            ),

        "message":
            finding.get(
                "message",
                finding.get(
                    "description",
                    "Security issue detected"
                )
            ),

        "exploitable":
            severity in {
                "CRITICAL",
                "HIGH"
            }
    }


# ============================================================
# THREAT ANALYSIS
# ============================================================

def analyze_threats(
    findings: list
):

    threats = []

    for finding in findings:

        threats.append(
            classify_threat(
                finding
            )
        )

    severity_counts = {

        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "UNKNOWN": 0
    }

    for threat in threats:

        severity = threat[
            "severity"
        ]

        if severity in severity_counts:

            severity_counts[
                severity
            ] += 1

    return {

        "totalThreats":
            len(threats),

        "severityCounts":
            severity_counts,

        "exploitableThreats":
            sum(
                1
                for threat in threats
                if threat["exploitable"]
            ),

        "threats":
            threats
    }