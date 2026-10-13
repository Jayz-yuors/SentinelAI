from ai.intelligence.risk.finding import (
    RiskFinding,
)


class FindingDeduplicator:

    def deduplicate(
        self,
        findings: list[RiskFinding],
    ) -> list[RiskFinding]:

        unique = {}

        for finding in findings:

            if not finding.fingerprint:

                raise ValueError(
                    "Finding fingerprint "
                    "must be generated "
                    "before deduplication."
                )

            if (
                finding.fingerprint
                not in unique
            ):

                unique[
                    finding.fingerprint
                ] = finding

            else:

                existing = unique[
                    finding.fingerprint
                ]

                existing.related_findings.append(
                    finding.tool
                )

                existing.confidence = max(
                    existing.confidence,
                    finding.confidence,
                )

        return list(
            unique.values()
        )