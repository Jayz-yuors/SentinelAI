import json

from ai.intelligence.risk.finding import RiskFinding


class SemgrepParser:

    def parse(self, raw_output: str) -> list[RiskFinding]:

        if not raw_output:
            return []

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            return []

        findings: list[RiskFinding] = []

        for item in data.get("results", []):

            extra = item.get("extra", {})

            metadata = extra.get(
                "metadata",
                {}
            )

            # Semgrep's metadata may contain:
            #
            # severity: WARNING / ERROR / INFO
            #
            # The SentinelAI internal contract is:
            #
            # critical / high / medium / low / info
            #
            raw_severity = (
                metadata.get("severity")
                or extra.get("severity")
                or "medium"
            )

            raw_severity = str(
                raw_severity
            ).strip().lower()

            # Normalize Semgrep's native levels.
            severity_map = {
                "error": "high",
                "warning": "high",
                "warn": "high",
                "info": "info",
                "information": "info",
                "critical": "critical",
                "high": "high",
                "medium": "medium",
                "low": "low",
            }

            severity = severity_map.get(
                raw_severity,
                "medium"
            )

            message = (
                extra.get("message")
                or "Static analysis finding."
            )

            file_path = item.get("path")

            start = item.get(
                "start",
                {}
            )

            line_number = start.get(
                "line"
            )

            rule_id = item.get(
                "check_id"
            )

            evidence = (
                extra.get("lines")
                or extra.get("metavars")
            )

            findings.append(
                RiskFinding(
                    source="semgrep",
                    tool="semgrep",
                    category="static_analysis",
                    severity=severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_number,
                    rule_id=rule_id,
                    evidence=(
                        str(evidence)
                        if evidence is not None
                        else None
                    ),
                    confidence=1.0,
                    metadata=metadata,
                )
            )

        return findings