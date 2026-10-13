from pathlib import Path

from ai.analyzer.code.parser import analyze_python_file


def analyze_code(repository_path: Path):

    result = []

    for file_path in repository_path.rglob("*.py"):

        if ".git" in file_path.parts:
            continue

        analysis = analyze_python_file(
            file_path
        )

        result.append({
            "file": str(
                file_path.relative_to(repository_path)
            ),
            "analysis": analysis
        })

    return result