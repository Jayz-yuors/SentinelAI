import hashlib
import re

from ai.intelligence.risk.finding import (
    RiskFinding,
)


def _normalize_text(
    value: str | None,
) -> str:

    if not value:
        return ""

    value = value.lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def generate_fingerprint(
    finding: RiskFinding,
) -> str:

    components = [

        _normalize_text(
            finding.file_path
        ),

        str(
            finding.line_number
            or ""
        ),

        _normalize_text(
            finding.category
        ),

        _normalize_text(
            finding.rule_id
        ),

        _normalize_text(
            finding.cve_id
        ),

        _normalize_text(
            finding.dependency
        ),

        _normalize_text(
            finding.message
        ),
    ]

    canonical = "|".join(
        components
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest()