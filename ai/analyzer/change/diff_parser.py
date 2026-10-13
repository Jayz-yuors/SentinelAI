from pathlib import Path

from ai.analyzer.code.parser import analyze_python_file


def analyze_imports(repository_path: Path):

    imports = {}

    for file_path in repository_path.rglob("*.py"):

        if ".git" in file_path.parts:
            continue

        analysis = analyze_python_file(
            file_path
        )

        relative_path = str(
            file_path.relative_to(repository_path)
        )

        imports[relative_path] = analysis[
            "imports"
        ]

    return imports