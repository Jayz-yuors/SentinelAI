from enum import IntEnum


class Severity(IntEnum):

    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


SEVERITY_ALIASES = {

    "info": Severity.INFO,
    "informational": Severity.INFO,

    "low": Severity.LOW,

    "medium": Severity.MEDIUM,
    "moderate": Severity.MEDIUM,

    "high": Severity.HIGH,

    "critical": Severity.CRITICAL,
}


def normalize_severity(
    value: str | int | None,
) -> Severity:

    if value is None:
        return Severity.INFO

    if isinstance(value, int):

        try:
            return Severity(value)

        except ValueError:
            return Severity.INFO

    normalized = (
        value.strip()
        .lower()
    )

    return SEVERITY_ALIASES.get(
        normalized,
        Severity.INFO,
    )


def severity_name(
    severity: Severity,
) -> str:

    return severity.name