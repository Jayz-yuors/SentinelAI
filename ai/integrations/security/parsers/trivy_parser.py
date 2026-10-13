import json

from ai.intelligence.risk.finding import RiskFinding


class TrivyParser:

    def parse(self, raw_output: str) -> list[RiskFinding]:

        if not raw_output:
            return []

        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            return []

        findings: list[RiskFinding] = []

        for result in data.get("Results", []):

            target = result.get("Target")

            # ---------------------------------------------------------
            # Vulnerabilities
            # ---------------------------------------------------------

            for vulnerability in result.get(
                "Vulnerabilities",
                []
            ):

                severity = (
                    vulnerability.get("Severity")
                    or "medium"
                ).lower()

                cve_id = (
                    vulnerability.get(
                        "VulnerabilityID"
                    )
                )

                message = (
                    vulnerability.get("Title")
                    or vulnerability.get("Description")
                    or "Vulnerability detected."
                )

                dependency = (
                    vulnerability.get("PkgName")
                )

                findings.append(
                    RiskFinding(
                        source="trivy",
                        tool="trivy",
                        category="vulnerability",
                        severity=severity,
                        message=message,
                        file_path=target,
                        rule_id=cve_id,
                        cve_id=cve_id,
                        dependency=dependency,
                        evidence=(
                            vulnerability.get(
                                "InstalledVersion"
                            )
                        ),
                        confidence=1.0,
                        metadata={
                            "installed_version":
                                vulnerability.get(
                                    "InstalledVersion"
                                ),
                            "fixed_version":
                                vulnerability.get(
                                    "FixedVersion"
                                ),
                            "primary_url":
                                vulnerability.get(
                                    "PrimaryURL"
                                ),
                        },
                    )
                )

            # ---------------------------------------------------------
            # Misconfigurations
            # ---------------------------------------------------------

            for misconfiguration in result.get(
                "Misconfigurations",
                []
            ):

                severity = (
                    misconfiguration.get("Severity")
                    or "medium"
                ).lower()

                rule_id = (
                    misconfiguration.get("ID")
                )

                message = (
                    misconfiguration.get("Title")
                    or misconfiguration.get("Message")
                    or "Misconfiguration detected."
                )

                findings.append(
                    RiskFinding(
                        source="trivy",
                        tool="trivy",
                        category="misconfiguration",
                        severity=severity,
                        message=message,
                        file_path=target,
                        rule_id=rule_id,
                        evidence=(
                            misconfiguration.get(
                                "Message"
                            )
                        ),
                        confidence=1.0,
                        metadata={
                            "resolution":
                                misconfiguration.get(
                                    "Resolution"
                                ),
                        },
                    )
                )

        return findings