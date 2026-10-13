from dataclasses import dataclass, field


@dataclass
class SecurityRiskModel:

    overall_score: int = 0

    overall_risk: str = "NONE"

    critical_findings: int = 0

    high_findings: int = 0

    medium_findings: int = 0

    low_findings: int = 0

    findings: list = field(
        default_factory=list
    )


    def add_findings(
        self,
        findings
    ):

        for finding in findings:

            severity = finding.get(
                "severity",
                "LOW"
            ).upper()

            self.findings.append(
                finding
            )

            if severity == "CRITICAL":
                self.critical_findings += 1

            elif severity == "HIGH":
                self.high_findings += 1

            elif severity == "MEDIUM":
                self.medium_findings += 1

            else:
                self.low_findings += 1


    def calculate_score(self):

        self.overall_score = (
            self.critical_findings * 10
            +
            self.high_findings * 7
            +
            self.medium_findings * 4
            +
            self.low_findings
        )

        if self.overall_score >= 30:
            self.overall_risk = "CRITICAL"

        elif self.overall_score >= 15:
            self.overall_risk = "HIGH"

        elif self.overall_score >= 5:
            self.overall_risk = "MEDIUM"

        elif self.overall_score > 0:
            self.overall_risk = "LOW"

        else:
            self.overall_risk = "NONE"


    def to_dict(self):

        return {
            "overallScore": self.overall_score,
            "overallRisk": self.overall_risk,
            "criticalFindings": (
                self.critical_findings
            ),
            "highFindings": (
                self.high_findings
            ),
            "mediumFindings": (
                self.medium_findings
            ),
            "lowFindings": (
                self.low_findings
            ),
            "findings": self.findings
        }