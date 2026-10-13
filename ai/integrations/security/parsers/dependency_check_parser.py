import json

from ai.intelligence.risk.finding import RiskFinding


class DependencyCheckParser:

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

        dependencies = data.get(
            "dependencies",
            []
        )

        for dependency_data in dependencies:

            dependency_name = (
                dependency_data.get(
                    "fileName"
                )
            )

            vulnerabilities = (
                dependency_data.get(
                    "vulnerabilities",
                    []
                )
            )

            for vulnerability in vulnerabilities:

                severity = (
                    vulnerability.get(
                        "severity"
                    )
                    or "medium"
                )

                severity = str(
                    severity
                ).strip().lower()

                severity_map = {
                    "critical": "critical",
                    "high": "high",
                    "medium": "medium",
                    "moderate": "medium",
                    "low": "low",
                    "info": "info",
                    "informational": "info",
                }

                severity = severity_map.get(
                    severity,
                    "medium"
                )

                cve_id = vulnerability.get(
                    "name"
                )

                description = (
                    vulnerability.get(
                        "description"
                    )
                    or vulnerability.get(
                        "source"
                    )
                    or "Dependency vulnerability detected."
                )

                cvss_score = None

                cvss_v3 = vulnerability.get(
                    "cvssv3"
                )

                if isinstance(
                    cvss_v3,
                    dict
                ):
                    cvss_score = cvss_v3.get(
                        "baseScore"
                    )

                findings.append(
                    RiskFinding(
                        source="dependency-check",
                        tool="dependency-check",
                        category="dependency",
                        severity=severity,
                        message=description,
                        file_path=dependency_name,
                        rule_id=cve_id,
                        cve_id=cve_id,
                        dependency=dependency_name,
                        evidence=description,
                        confidence=1.0,
                        metadata={
                            "cvss_score": cvss_score,
                        },
                    )
                )

        return findings