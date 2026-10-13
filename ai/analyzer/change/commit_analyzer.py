import subprocess
from pathlib import Path


def get_latest_commit(repository_path: Path):

    command = [
        "git",
        "-C",
        str(repository_path),
        "log",
        "-1",
        "--pretty=format:%H|%an|%ad|%s"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    parts = result.stdout.split("|", 3)

    if len(parts) != 4:
        return None

    return {
        "hash": parts[0],
        "author": parts[1],
        "date": parts[2],
        "message": parts[3]
    }