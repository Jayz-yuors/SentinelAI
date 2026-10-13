SEVERITY_WEIGHTS = {

    "CRITICAL": 10,

    "HIGH": 8,

    "MEDIUM": 5,

    "LOW": 2,

    "UNKNOWN": 1
}


# ============================================================
# FILE RISK
# ============================================================

def calculate_file_risk(
    findings: list
):

    scores = {}

    for finding in findings:

        file_path = finding.get(
            "file",
            "unknown"
        )

        severity = finding.get(
            "severity",
            "UNKNOWN"
        ).upper()

        score = SEVERITY_WEIGHTS.get(
            severity,
            1
        )

        scores[file_path] = (
            scores.get(
                file_path,
                0
            )
            + score
        )

    results = []

    for file_path, score in scores.items():

        if score >= 15:

            risk = "CRITICAL"

        elif score >= 8:

            risk = "HIGH"

        elif score >= 4:

            risk = "MEDIUM"

        else:

            risk = "LOW"

        results.append({

            "file":
                file_path,

            "score":
                score,

            "risk":
                risk
        })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )


# ============================================================
# REPOSITORY RISK
# ============================================================

def calculate_security_risk(
    findings: list
):

    total_score = sum(

        SEVERITY_WEIGHTS.get(
            finding.get(
                "severity",
                "UNKNOWN"
            ).upper(),
            1
        )

        for finding in findings
    )

    if total_score >= 30:

        overall_risk = "CRITICAL"

    elif total_score >= 15:

        overall_risk = "HIGH"

    elif total_score >= 5:

        overall_risk = "MEDIUM"

    else:

        overall_risk = "LOW"

    return {

        "overallScore":
            total_score,

        "overallRisk":
            overall_risk,

        "totalFindings":
            len(findings),

        "fileRisks":
            calculate_file_risk(
                findings
            )
    }