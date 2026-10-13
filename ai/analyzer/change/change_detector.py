import subprocess
from pathlib import Path


def detect_changes(repository_path: Path):

    command = [
        "git",
        "-C",
        str(repository_path),
        "diff",
        "--name-status",
        "HEAD~1",
        "HEAD"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return []

    changes = []

    for line in result.stdout.splitlines():

        parts = line.split("\t")

        if len(parts) >= 2:

            changes.append({
                "status": parts[0],
                "file": parts[1]
            })

    return changes