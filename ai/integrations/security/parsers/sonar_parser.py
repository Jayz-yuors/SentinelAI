import json

from ai.intelligence.risk.finding import RiskFinding


class SonarParser:

    def parse(
        self,
        raw_output: str
    ) -> list[RiskFinding]:

        if not raw_output:
            return []

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            return []

        findings: list[RiskFinding] = []

        issues = data.get(
            "issues",
            []
        )

        for issue in issues:

            raw_severity = (
                issue.get("severity")
                or "medium"
            )

            raw_severity = str(
                raw_severity
            ).strip().lower()

            severity_map = {
                "blocker": "critical",
                "critical": "critical",
                "major": "high",
                "high": "high",
                "minor": "medium",
                "medium": "medium",
                "low": "low",
                "info": "info",
                "informational": "info",
            }

            severity = severity_map.get(
                raw_severity,
                "medium"
            )

            rule_id = issue.get(
                "rule"
            )

            message = (
                issue.get("message")
                or "SonarQube issue detected."
            )

            component = issue.get(
                "component"
            )

            line_number = issue.get(
                "line"
            )

            issue_type = (
                issue.get("type")
                or "CODE_SMELL"
            ).lower()

            findings.append(
                RiskFinding(
                    source="sonar",
                    tool="sonar",
                    category=issue_type,
                    severity=severity,
                    message=message,
                    file_path=component,
                    line_number=line_number,
                    rule_id=rule_id,
                    evidence=message,
                    confidence=1.0,
                    metadata={
                        "project":
                            issue.get(
                                "project"
                            ),
                        "status":
                            issue.get(
                                "status"
                            ),
                        "effort":
                            issue.get(
                                "effort"
                            ),
                        "debt":
                            issue.get(
                                "debt"
                            ),
                    },
                )
            )

        return findings