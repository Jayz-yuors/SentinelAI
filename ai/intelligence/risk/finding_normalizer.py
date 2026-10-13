from typing import Any

from ai.intelligence.risk.finding import RiskFinding


class FindingNormalizer:

    @staticmethod
    def _get(
        finding: Any,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read a field from either a RiskFinding object
        or a dictionary.

        RiskFinding is the canonical SentinelAI representation,
        but accepting dictionaries keeps the normalizer
        compatible with scanner adapters and legacy callers.
        """

        if isinstance(finding, RiskFinding):
            return getattr(
                finding,
                key,
                default,
            )

        if isinstance(finding, dict):
            return finding.get(
                key,
                default,
            )

        return getattr(
            finding,
            key,
            default,
        )

    @classmethod
    def normalize(
        cls,
        finding: Any,
    ) -> RiskFinding:

        # -------------------------------------------------------------
        # Already normalized
        # -------------------------------------------------------------

        if isinstance(
            finding,
            RiskFinding,
        ):
            return finding

        # -------------------------------------------------------------
        # Basic fields
        # -------------------------------------------------------------

        source = cls._get(
            finding,
            "source",
            "unknown",
        )

        tool = cls._get(
            finding,
            "tool",
            source,
        )

        category = cls._get(
            finding,
            "category",
            "unknown",
        )

        severity = cls._get(
            finding,
            "severity",
            "medium",
        )

        message = cls._get(
            finding,
            "message",
            "Security finding detected.",
        )

        file_path = cls._get(
            finding,
            "file_path",
        )

        line_number = cls._get(
            finding,
            "line_number",
        )

        rule_id = cls._get(
            finding,
            "rule_id",
        )

        cve_id = cls._get(
            finding,
            "cve_id",
        )

        dependency = cls._get(
            finding,
            "dependency",
        )

        evidence = cls._get(
            finding,
            "evidence",
        )

        confidence = cls._get(
            finding,
            "confidence",
            1.0,
        )

        fingerprint = cls._get(
            finding,
            "fingerprint",
        )

        related_findings = cls._get(
            finding,
            "related_findings",
            [],
        )

        metadata = cls._get(
            finding,
            "metadata",
            {},
        )

        # -------------------------------------------------------------
        # Normalize severity
        # -------------------------------------------------------------

        severity = str(
            severity
        ).strip().lower()

        severity_map = {
            "critical": "critical",
            "crit": "critical",

            "high": "high",
            "error": "high",

            "medium": "medium",
            "moderate": "medium",
            "warning": "medium",
            "warn": "medium",

            "low": "low",

            "info": "info",
            "informational": "info",
        }

        severity = severity_map.get(
            severity,
            "medium",
        )

        # -------------------------------------------------------------
        # Normalize confidence
        # -------------------------------------------------------------

        try:
            confidence = float(
                confidence
            )
        except (
            TypeError,
            ValueError,
        ):
            confidence = 1.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        # -------------------------------------------------------------
        # Normalize collections
        # -------------------------------------------------------------

        if related_findings is None:
            related_findings = []

        if metadata is None:
            metadata = {}

        # -------------------------------------------------------------
        # Construct canonical RiskFinding
        # -------------------------------------------------------------

        return RiskFinding(
            source=source,
            tool=tool,
            category=category,
            severity=severity,
            message=message,
            file_path=file_path,
            line_number=line_number,
            rule_id=rule_id,
            cve_id=cve_id,
            dependency=dependency,
            evidence=evidence,
            confidence=confidence,
            fingerprint=fingerprint,
            related_findings=list(
                related_findings
            ),
            metadata=dict(
                metadata
            ),
        )

    @classmethod
    def normalize_many(
        cls,
        findings: list[Any],
    ) -> list[RiskFinding]:

        if not findings:
            return []

        return [
            cls.normalize(
                finding
            )
            for finding in findings
        ]