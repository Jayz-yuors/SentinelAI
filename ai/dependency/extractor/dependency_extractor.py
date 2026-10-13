from pathlib import Path

from ai.dependency.extractor.python_dependencies import (
    extract_python_dependencies
)

from ai.dependency.extractor.java_dependencies import (
    extract_java_dependencies
)

from ai.dependency.extractor.javascript_dependencies import (
    extract_javascript_dependencies
)


LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}


def get_language(file_path: Path):
    """
    Determine the programming language from file extension.
    """

    return LANGUAGE_EXTENSIONS.get(
        file_path.suffix.lower()
    )


def extract_file_dependencies(file_path: Path):
    """
    Extract dependencies from a single source file.
    """

    language = get_language(file_path)

    if language == "Python":
        return extract_python_dependencies(file_path)

    if language == "Java":
        return extract_java_dependencies(file_path)

    if language in {"JavaScript", "TypeScript"}:
        return extract_javascript_dependencies(file_path)

    return []


def _build_repository_file_index(repository_path: Path):
    """
    Build an index of source files inside the repository.

    The index allows us to determine whether a dependency
    refers to an internal project file or an external package.
    """

    index = {}

    for file_path in repository_path.rglob("*"):

        if not file_path.is_file():
            continue

        if ".git" in file_path.parts:
            continue

        relative = file_path.relative_to(
            repository_path
        )

        normalized = str(relative).replace("\\", "/")

        index[normalized] = file_path

    return index


def _normalize_dependency_name(dependency: str):
    """
    Normalize dependency strings for comparison.
    """

    dependency = dependency.strip()

    dependency = dependency.replace("\\", "/")

    return dependency


def _possible_internal_paths(
    source_file: Path,
    dependency: str,
    repository_path: Path
):
    """
    Generate possible repository paths for a dependency.
    """

    dependency = _normalize_dependency_name(
        dependency
    )

    candidates = []

    source_directory = source_file.parent

    # Relative JavaScript / TypeScript imports
    if dependency.startswith("."):

        base = (
            source_directory / dependency
        ).resolve()

        candidates.extend([
            base,
            Path(str(base) + ".js"),
            Path(str(base) + ".jsx"),
            Path(str(base) + ".ts"),
            Path(str(base) + ".tsx"),
            base / "index.js",
            base / "index.jsx",
            base / "index.ts",
            base / "index.tsx",
        ])

    # Direct repository-relative path
    else:

        base = (
            repository_path / dependency
        ).resolve()

        candidates.extend([
            base,
            Path(str(base) + ".py"),
            Path(str(base) + ".java"),
            Path(str(base) + ".js"),
            Path(str(base) + ".jsx"),
            Path(str(base) + ".ts"),
            Path(str(base) + ".tsx"),
        ])

    return candidates


def resolve_dependency(
    source_file: Path,
    dependency: str,
    repository_path: Path
):
    """
    Determine whether a dependency is internal or external.

    Returns:
        {
            "name": dependency,
            "type": "internal" / "external",
            "resolvedFile": ...
        }
    """

    dependency = _normalize_dependency_name(
        dependency
    )

    candidates = _possible_internal_paths(
        source_file,
        dependency,
        repository_path
    )

    for candidate in candidates:

        try:

            candidate.relative_to(
                repository_path
            )

        except ValueError:

            continue

        if candidate.is_file():

            return {
                "name": dependency,
                "type": "internal",
                "resolvedFile": str(
                    candidate.relative_to(
                        repository_path
                    )
                ).replace("\\", "/")
            }

    return {
        "name": dependency,
        "type": "external",
        "resolvedFile": None
    }


def extract_repository_dependencies(
    repository_path: Path
):
    """
    Extract dependencies from the complete repository.
    """

    repository_path = Path(
        repository_path
    )

    file_dependencies = []

    for file_path in repository_path.rglob("*"):

        if not file_path.is_file():
            continue

        if ".git" in file_path.parts:
            continue

        language = get_language(file_path)

        if language is None:
            continue

        dependencies = extract_file_dependencies(
            file_path
        )

        relative_file = str(
            file_path.relative_to(
                repository_path
            )
        ).replace("\\", "/")

        resolved_dependencies = []

        for dependency in dependencies:

            resolved = resolve_dependency(
                file_path,
                dependency,
                repository_path
            )

            resolved_dependencies.append(
                resolved
            )

        file_dependencies.append({
            "file": relative_file,
            "language": language,
            "dependencies": resolved_dependencies
        })

    return file_dependencies