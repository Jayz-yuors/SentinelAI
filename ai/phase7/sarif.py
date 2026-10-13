def risk_to_sarif(profile) -> dict:
    """
    Convert a SentinelAI RiskProfile into SARIF 2.1.0 format.

    This function is intentionally independent of the rest of Phase 7 so
    it can be used by the artifact/reporting layer without modifying the
    existing risk engine.
    """

    results = []

    for finding in getattr(profile, "findings", []):
        severity = str(
            getattr(finding, "severity", "warning")
        ).lower()

        # Map SentinelAI severity -> SARIF level
        level = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note",
        }.get(severity, "warning")

        rule_id = (
            getattr(finding, "rule_id", None)
            or getattr(finding, "category", None)
            or "sentinelai"
        )

        message = getattr(
            finding,
            "message",
            "SentinelAI security finding",
        )

        result = {
            "ruleId": str(rule_id),
            "level": level,
            "message": {
                "text": str(message)
            },
        }

        # ---------------------------------------------------------
        # Optional source-code location
        # ---------------------------------------------------------

        file_path = getattr(
            finding,
            "file_path",
            None,
        )

        line_number = getattr(
            finding,
            "line_number",
            None,
        )

        if file_path:
            physical_location = {
                "artifactLocation": {
                    "uri": str(file_path)
                }
            }

            if line_number:
                physical_location["region"] = {
                    "startLine": int(line_number)
                }

            result["locations"] = [
                {
                    "physicalLocation": physical_location
                }
            ]

        results.append(result)

    # -------------------------------------------------------------
    # Complete SARIF 2.1.0 document
    # -------------------------------------------------------------

    return {
        "$schema": (
            "https://json.schemastore.org/"
            "sarif-2.1.0.json"
        ),
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SentinelAI",
                        "informationUri": (
                            "https://github.com/"
                            "Jayz-yuors/SentinelAI"
                        ),
                    }
                },
                "results": results,
            }
        ],
    }