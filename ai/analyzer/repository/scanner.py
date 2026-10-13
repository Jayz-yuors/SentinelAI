import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from ai.analyzer.code.structure import analyze_code
from ai.analyzer.code.imports import analyze_imports
from ai.analyzer.change.commit_analyzer import get_latest_commit
from ai.analyzer.change.impact import calculate_impact

# ============================================================
# PHASE 2
# ============================================================

from ai.dependency.dependency_pipeline import analyze_dependencies
from ai.security.external.tool_service import (
    run_external_security_tools
)
# ============================================================
# PHASE 3
# ============================================================

from ai.security.security_pipeline import (
    analyze_security_repository
)


# ============================================================
# DIRECTORIES TO IGNORE
# ============================================================

IGNORE_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "target",
    "build",
    "dist",
    ".idea",
    ".vscode",
}


# ============================================================
# SUPPORTED PROGRAMMING LANGUAGES
# ============================================================

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".kt": "Kotlin",
    ".swift": "Swift",
}


# ============================================================
# MAXIMUM FILE SIZE
# ============================================================

MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# GIT CLONE
# ============================================================

def clone_repository(
    repository_url: str,
    branch: str,
    destination: str
):
    command = [
        "git",
        "clone",
        "--depth",
        "20",
        "--branch",
        branch,
        repository_url,
        destination
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git clone failed:\n"
            f"{result.stderr.strip()}"
        )


# ============================================================
# FILE COLLECTION
# ============================================================

def collect_files(repository_path: Path):

    files = []

    for root, directories, filenames in os.walk(
        repository_path
    ):

        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORE_DIRECTORIES
        ]

        for filename in filenames:

            path = Path(root) / filename

            try:
                if path.stat().st_size > MAX_FILE_SIZE:
                    continue

            except OSError:
                continue

            files.append(path)

    return files


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_languages(files):

    languages = set()

    for file in files:

        extension = file.suffix.lower()

        if extension in LANGUAGE_EXTENSIONS:

            languages.add(
                LANGUAGE_EXTENSIONS[extension]
            )

    return sorted(languages)


# ============================================================
# FILE TYPE STATISTICS
# ============================================================

def count_file_types(files):

    file_types = {}

    for file in files:

        extension = file.suffix.lower()

        if not extension:
            extension = "[no extension]"

        file_types[extension] = (
            file_types.get(extension, 0) + 1
        )

    return dict(
        sorted(
            file_types.items(),
            key=lambda item: item[0]
        )
    )


# ============================================================
# CHANGED FILES
# ============================================================

def get_changed_files(repository_path: Path):

    command = [
        "git",
        "-C",
        str(repository_path),
        "diff",
        "--name-only",
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

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


# ============================================================
# REPOSITORY NAME
# ============================================================

def get_repository_name(repository_url: str):

    repository_name = (
        repository_url
        .rstrip("/")
        .split("/")[-1]
    )

    if repository_name.endswith(".git"):
        repository_name = repository_name[:-4]

    return repository_name


# ============================================================
# MAIN REPOSITORY ANALYSIS
# ============================================================

def analyze_repository(
    repository_url: str,
    branch: str
):

    temporary_directory = tempfile.mkdtemp(
        prefix="sentinelai_"
    )

    repository_path = (
        Path(temporary_directory)
        / "repository"
    )

    repository_name = get_repository_name(
        repository_url
    )

    try:

        # ====================================================
        # PHASE 1
        # ====================================================

        # ----------------------------------------------------
        # 1. Clone repository
        # ----------------------------------------------------

        clone_repository(
            repository_url,
            branch,
            str(repository_path)
        )

        # ----------------------------------------------------
        # 2. Collect files
        # ----------------------------------------------------

        files = collect_files(
            repository_path
        )

        # ----------------------------------------------------
        # 3. Detect languages
        # ----------------------------------------------------

        languages = detect_languages(
            files
        )

        # ----------------------------------------------------
        # 4. File statistics
        # ----------------------------------------------------

        file_types = count_file_types(
            files
        )

        # ----------------------------------------------------
        # 5. Git changed files
        # ----------------------------------------------------

        changed_files = get_changed_files(
            repository_path
        )

        # ----------------------------------------------------
        # 6. Code structure analysis
        # ----------------------------------------------------

        code_structure = analyze_code(
            repository_path
        )

        # ----------------------------------------------------
        # 7. Import analysis
        # ----------------------------------------------------

        import_analysis = analyze_imports(
            repository_path
        )

        # ----------------------------------------------------
        # 8. Latest commit analysis
        # ----------------------------------------------------

        latest_commit = get_latest_commit(
            repository_path
        )

        # ----------------------------------------------------
        # 9. Change impact analysis
        # ----------------------------------------------------

        impact_analysis = calculate_impact(
            repository_path
        )

        # ====================================================
        # PHASE 2
        # ====================================================

        # ----------------------------------------------------
        # 10. Dependency analysis
        # ----------------------------------------------------

        dependency_analysis = analyze_dependencies(
            repository_path
        )

        # ====================================================
        # PHASE 3
        # ====================================================

        # ----------------------------------------------------
        # 11. Security analysis
        #
        # Phase 3 receives the Phase 2 dependency context.
        # ----------------------------------------------------

        security_analysis = analyze_security_repository(
            repository_path,
            dependency_analysis=dependency_analysis
        )
        external_security_tools = (
            run_external_security_tools(
                repository_path
            )
        )
        security_analysis[
            "securityAnalysis"
        ]["externalTools"] = (
            external_security_tools
        )
        # ====================================================
        # FINAL UNIFIED RESULT
        # ====================================================

        return {

            "success": True,

            # =================================================
            # REPOSITORY INFORMATION
            # =================================================

            "repositoryUrl": repository_url,

            "repositoryName": repository_name,

            "branch": branch,

            # =================================================
            # PHASE 1 RESULTS
            # =================================================

            "totalFiles": len(files),

            "languages": languages,

            "fileTypes": file_types,

            "changedFiles": changed_files,

            "codeStructure": code_structure,

            "imports": import_analysis,

            "latestCommit": latest_commit,

            "impactAnalysis": impact_analysis,

            # =================================================
            # PHASE 2 RESULTS
            # =================================================

            "dependencyExtraction":
                dependency_analysis.get(
                    "dependencyExtraction",
                    []
                ),

            "dependencyGraph":
                dependency_analysis.get(
                    "dependencyGraph",
                    {
                        "nodes": [],
                        "edges": []
                    }
                ),

            "graphAnalysis":
                dependency_analysis.get(
                    "graphAnalysis",
                    {
                        "totalNodes": 0,
                        "totalEdges": 0,
                        "dependencyCounts": {},
                        "highImpactFiles": [],
                        "circularDependencies": []
                    }
                ),

            "dependencyRisk":
                dependency_analysis.get(
                    "dependencyRisk",
                    {
                        "overallScore": 0,
                        "overallRisk": "UNKNOWN",
                        "fileRisks": []
                    }
                ),

            # =================================================
            # PHASE 3 RESULTS
            # =================================================

            "securityAnalysis":
                security_analysis.get(
                    "securityAnalysis",
                    {
                        "secrets": {},
                        "dependencyVulnerabilities": {},
                        "cves": {},
                        "staticAnalysis": {},
                        "threatAnalysis": {},
                        "risk": {},
                        "findings": []
                    }
                ),

            # =================================================
            # FINAL MESSAGE
            # =================================================

            "message":
                "Phase 1 + Phase 2 + Phase 3 analysis completed successfully"
        }

    except Exception as error:

        return {

            "success": False,

            # =================================================
            # REPOSITORY INFORMATION
            # =================================================

            "repositoryUrl": repository_url,

            "repositoryName": repository_name,

            "branch": branch,

            # =================================================
            # PHASE 1 DEFAULTS
            # =================================================

            "totalFiles": 0,

            "languages": [],

            "fileTypes": {},

            "changedFiles": [],

            "codeStructure": [],

            "imports": {},

            "latestCommit": None,

            "impactAnalysis": {
                "changed_file_count": 0,
                "impacted_file_types": [],
                "changes": []
            },

            # =================================================
            # PHASE 2 DEFAULTS
            # =================================================

            "dependencyExtraction": [],

            "dependencyGraph": {
                "nodes": [],
                "edges": []
            },

            "graphAnalysis": {
                "totalNodes": 0,
                "totalEdges": 0,
                "dependencyCounts": {},
                "highImpactFiles": [],
                "circularDependencies": []
            },

            "dependencyRisk": {
                "overallScore": 0,
                "overallRisk": "UNKNOWN",
                "fileRisks": []
            },

            # =================================================
            # PHASE 3 DEFAULTS
            # =================================================

            "securityAnalysis": {
                "secrets": {},
                "dependencyVulnerabilities": {},
                "cves": {},
                "staticAnalysis": {},
                "threatAnalysis": {},
                "risk": {},
                "findings": []
            },

            # =================================================
            # ERROR
            # =================================================

            "message": str(error)
        }

    finally:

        # ====================================================
        # CLEANUP CLONED REPOSITORY
        # ====================================================

        shutil.rmtree(
            temporary_directory,
            ignore_errors=True
        )