import re
from pathlib import Path


IMPORT_PATTERN = re.compile(
    r"^\s*import\s+(?:static\s+)?"
    r"([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)*)\s*;"
)


def extract_java_dependencies(
    file_path: Path
):
    """
    Extract Java import statements.
    """

    try:

        source = file_path.read_text(
            encoding="utf-8"
        )

    except (OSError, UnicodeDecodeError):

        return []

    dependencies = set()

    for line in source.splitlines():

        match = IMPORT_PATTERN.match(
            line
        )

        if match:

            dependencies.add(
                match.group(1)
            )

    return sorted(
        dependencies
    )