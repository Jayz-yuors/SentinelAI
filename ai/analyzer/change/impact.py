from pathlib import Path

from ai.analyzer.change.change_detector import detect_changes


def calculate_impact(repository_path: Path):

    changes = detect_changes(
        repository_path
    )

    impacted_extensions = set()

    for change in changes:

        file_path = Path(
            change["file"]
        )

        if file_path.suffix:
            impacted_extensions.add(
                file_path.suffix
            )

    return {
        "changed_file_count": len(changes),
        "impacted_file_types": sorted(
            impacted_extensions
        ),
        "changes": changes
    }