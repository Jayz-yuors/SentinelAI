import re
from pathlib import Path


IMPORT_PATTERN = re.compile(
    r"""import\s+(?:[\s\S]*?\s+from\s+)?["']([^"']+)["']"""
)

REQUIRE_PATTERN = re.compile(
    r"""require\s*\(\s*["']([^"']+)["']\s*\)"""
)


def extract_javascript_dependencies(
    file_path: Path
):
    """
    Extract JavaScript / TypeScript dependencies.

    Supports:
        import x from "package"
        import "package"
        require("package")
    """

    try:

        source = file_path.read_text(
            encoding="utf-8"
        )

    except (OSError, UnicodeDecodeError):

        return []

    dependencies = set()

    for match in IMPORT_PATTERN.finditer(
        source
    ):

        dependencies.add(
            match.group(1)
        )

    for match in REQUIRE_PATTERN.finditer(
        source
    ):

        dependencies.add(
            match.group(1)
        )

    return sorted(
        dependencies
    )