from ai.intelligence.risk.finding import RiskFinding

from ai.intelligence.risk.finding_normalizer import (
    FindingNormalizer,
)

from ai.intelligence.risk.fingerprint import (
    generate_fingerprint,
)

from ai.intelligence.risk.correlation import (
    FindingCorrelator,
)

from ai.intelligence.risk.deduplication import (
    FindingDeduplicator,
)

from ai.intelligence.risk.risk_profile import (
    RiskProfile,
)

from ai.intelligence.risk.risk_score import (
    calculate_risk_score,
    calculate_severity_counts,
    risk_level,
)


class UnifiedRiskEngine:

    def __init__(self):

        self.normalizer = FindingNormalizer()

        self.correlator = FindingCorrelator()

        self.deduplicator = FindingDeduplicator()

    def analyze(
        self,
        findings: list[RiskFinding],
    ) -> RiskProfile:

        # =============================================================
        # 1. NORMALIZE FINDINGS
        # =============================================================

        normalized_findings = (
            self.normalizer.normalize_many(
                findings
            )
        )

        # =============================================================
        # 2. GENERATE FINGERPRINTS
        #
        # Fingerprints are required by the deduplicator.
        # =============================================================

        for finding in normalized_findings:

            if not finding.fingerprint:

                finding.fingerprint = (
                    generate_fingerprint(
                        finding
                    )
                )

        # =============================================================
        # 3. CORRELATE FINDINGS
        #
        # correlate() returns:
        #
        # [
        #     [finding1, finding2],
        #     [finding3, finding4]
        # ]
        #
        # It intentionally returns only groups containing more than
        # one finding.
        # =============================================================

        correlation_groups = (
            self.correlator.correlate(
                normalized_findings
            )
        )

        # =============================================================
        # 4. FLATTEN CORRELATED FINDINGS
        #
        # Deduplicator expects:
        #
        # list[RiskFinding]
        #
        # NOT:
        #
        # list[list[RiskFinding]]
        # =============================================================

        correlated_findings = []

        for group in correlation_groups:

            correlated_findings.extend(
                group
            )

        # =============================================================
        # 5. PRESERVE NON-CORRELATED FINDINGS
        #
        # The correlator only returns groups with 2+ findings.
        # Therefore singleton findings must be added back.
        # =============================================================

        correlated_ids = {
            id(finding)
            for finding in correlated_findings
        }

        for finding in normalized_findings:

            if id(finding) not in correlated_ids:

                correlated_findings.append(
                    finding
                )

        # =============================================================
        # 6. DEDUPLICATE
        # =============================================================

        unique_findings = (
            self.deduplicator.deduplicate(
                correlated_findings
            )
        )

        # =============================================================
        # 7. CALCULATE OVERALL RISK SCORE
        # =============================================================

        overall_score = calculate_risk_score(
            unique_findings
        )

        # =============================================================
        # 8. CALCULATE RISK LEVEL
        # =============================================================

        overall_level = risk_level(
            overall_score
        )

        # =============================================================
        # 9. SEVERITY COUNTS
        # =============================================================

        severity_counts = (
            calculate_severity_counts(
                unique_findings
            )
        )

        # =============================================================
        # 10. CATEGORY SCORES
        #
        # Security:
        #   secrets, vulnerabilities, misconfigurations,
        #   static analysis, etc.
        #
        # Dependency:
        #   dependency-related findings.
        #
        # Code:
        #   static analysis / code quality findings.
        # =============================================================

        security_findings = []

        dependency_findings = []

        code_findings = []

        for finding in unique_findings:

            category = (
                str(
                    finding.category
                )
                .strip()
                .lower()
            )

            if category == "dependency":

                dependency_findings.append(
                    finding
                )

            elif category in {
                "static_analysis",
                "code",
                "code_smell",
                "bug",
                "vulnerability",
            }:

                code_findings.append(
                    finding
                )

            else:

                security_findings.append(
                    finding
                )

        security_score = calculate_risk_score(
            security_findings
        )

        dependency_score = calculate_risk_score(
            dependency_findings
        )

        code_score = calculate_risk_score(
            code_findings
        )

        # =============================================================
        # 11. AFFECTED FILES
        # =============================================================

        affected_files = {
            finding.file_path
            for finding in unique_findings
            if finding.file_path
        }

        # =============================================================
        # 12. AFFECTED DEPENDENCIES
        # =============================================================

        affected_dependencies = {
            finding.dependency
            for finding in unique_findings
            if finding.dependency
        }

        # =============================================================
        # 13. TOP RISKS
        # =============================================================

        sorted_findings = sorted(
            unique_findings,
            key=lambda finding: (
                calculate_risk_score(
                    [finding]
                ),
                finding.confidence,
            ),
            reverse=True,
        )

        top_risks = []

        for finding in sorted_findings[:5]:

            top_risks.append(
                {
                    "fingerprint":
                        finding.fingerprint,

                    "severity":
                        finding.severity,

                    "category":
                        finding.category,

                    "tool":
                        finding.tool,

                    "message":
                        finding.message,

                    "file_path":
                        finding.file_path,

                    "line_number":
                        finding.line_number,

                    "score":
                        calculate_risk_score(
                            [finding]
                        ),
                }
            )

        # =============================================================
        # 14. RISK DRIVERS
        # =============================================================

        risk_drivers = []

        for finding in sorted_findings[:5]:

            driver = (
                f"{finding.severity.upper()}: "
                f"{finding.message}"
            )

            risk_drivers.append(
                driver
            )

        # =============================================================
        # 15. BUILD FINAL RISK PROFILE
        # =============================================================

        return RiskProfile(

            overall_score=overall_score,

            overall_level=overall_level,

            security_score=security_score,

            dependency_score=dependency_score,

            code_score=code_score,

            repository_score=overall_score,

            severity_counts=severity_counts,

            finding_count=len(
                unique_findings
            ),

            affected_files=len(
                affected_files
            ),

            affected_dependencies=len(
                affected_dependencies
            ),

            top_risks=top_risks,

            risk_drivers=risk_drivers,

            findings=unique_findings,
        )