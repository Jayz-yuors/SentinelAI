from collections import defaultdict

from ai.intelligence.risk.finding import (
    RiskFinding,
)


class FindingCorrelator:

    def correlate(
        self,
        findings: list[RiskFinding],
    ) -> list[list[RiskFinding]]:

        groups = defaultdict(list)

        for finding in findings:

            key = self._correlation_key(
                finding
            )

            groups[key].append(
                finding
            )

        return [
            group
            for group in groups.values()
            if len(group) > 1
        ]

    @staticmethod
    def _correlation_key(
        finding: RiskFinding,
    ) -> tuple:

        return (
            finding.file_path,
            finding.line_number,
            finding.category,
        )