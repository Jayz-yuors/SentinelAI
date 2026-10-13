#!/usr/bin/env python3
"""
SentinelAI Project Progress Tracker

Run this file from anywhere:

    python sentinelai_progress_tracker.py

By default it scans:
C:\\Users\\Shruti\\jk\\Python\\Python_GUI\\Project_series\\11.SentiNelAI

You can also provide another project path:

    python sentinelai_progress_tracker.py "C:\\path\\to\\11.SentiNelAI"

It creates:
    SENTINELAI_PROGRESS.md   -> easiest file to share for project-progress review
    SENTINELAI_PROGRESS.json -> machine-readable progress data
    SENTINELAI_TREE.txt      -> current folder/file tree

IMPORTANT:
- Folder/file existence is detected automatically.
- Functional completion cannot be perfectly inferred from a folder tree.
- The MILESTONES section below contains lightweight checks for important functionality.
- Update/add checks as the project grows.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path(
    r"C:\Users\Shruti\jk\Python\Python_GUI\Project_series\11.SentiNelAI"
)

# ---------------------------------------------------------------------
# IMPORTANT: These are the project milestones we will use to judge
# SentinelAI progress. Keep this list aligned with the FINAL architecture.
# ---------------------------------------------------------------------

MILESTONES = [
    {
        "id": "M01",
        "name": "Project and Git foundation",
        "area": "Foundation",
        "checks": [
            "README.md",
            ".git",
        ],
    },
    {
        "id": "M02",
        "name": "Spring Boot backend foundation",
        "area": "Backend",
        "checks": [
            "backend/pom.xml",
            "backend/src/main/java/com/sentinelai/backend/BackendApplication.java",
            "backend/src/main/resources/application.yaml",
        ],
    },
    {
        "id": "M03",
        "name": "Backend common infrastructure",
        "area": "Backend",
        "checks": [
            "backend/src/main/java/com/sentinelai/backend/common/config/CorsConfig.java",
            "backend/src/main/java/com/sentinelai/backend/common/constants/AppConstants.java",
            "backend/src/main/java/com/sentinelai/backend/common/exception/GlobalExceptionHandler.java",
        ],
    },
    {
        "id": "M04",
        "name": "Repository integration",
        "area": "Core",
        "checks": [
            "backend/src/main/java/com/sentinelai/backend/repository",
            "ai/analyzer/repository",
        ],
    },
    {
        "id": "M05",
        "name": "AI API",
        "area": "AI",
        "checks": [
            "ai/requirements.txt",
            "ai/api/main.py",
        ],
    },
    {
        "id": "M06",
        "name": "Repository/code/change analysis",
        "area": "AI",
        "checks": [
            "ai/analyzer/repository",
            "ai/analyzer/code",
            "ai/analyzer/change",
        ],
    },
    {
        "id": "M07",
        "name": "Dependency intelligence",
        "area": "AI",
        "checks": [
            "ai/dependency/extractor",
            "ai/dependency/graph",
        ],
    },
    {
        "id": "M08",
        "name": "Security intelligence",
        "area": "Security",
        "checks": [
            "ai/security",
            "security",
        ],
    },
    {
        "id": "M09",
        "name": "ML risk prediction",
        "area": "AI/ML",
        "checks": [
            "ai/prediction",
            "ai/models",
            "ai/data",
        ],
    },
    {
        "id": "M10",
        "name": "AI decision engine",
        "area": "AI",
        "checks": [
            "ai/decision/rules",
            "ai/decision/scoring",
            "ai/decision/engine",
        ],
    },
    {
        "id": "M11",
        "name": "Adaptive testing",
        "area": "CI/CD",
        "checks": [
            "ai/testing/selector",
            "ai/testing/prioritizer",
        ],
    },
    {
        "id": "M12",
        "name": "CI/CD execution layer",
        "area": "CI/CD",
        "checks": [
            "pipeline/github/workflows",
            "pipeline/scripts/build",
            "pipeline/scripts/test",
            "pipeline/scripts/security",
            "pipeline/scripts/deploy",
        ],
    },
    {
        "id": "M13",
        "name": "Database infrastructure",
        "area": "Infrastructure",
        "checks": [
            "database/postgres",
            "database/neo4j",
            "database/redis",
        ],
    },
    {
        "id": "M14",
        "name": "Containerization and deployment",
        "area": "Deployment",
        "checks": [
            "deployment/docker",
            "deployment/compose/docker-compose.yml",
            "deployment/kubernetes",
            "deployment/helm",
        ],
    },
    {
        "id": "M15",
        "name": "Monitoring and observability",
        "area": "Monitoring",
        "checks": [
            "monitoring/prometheus",
            "monitoring/grafana",
            "monitoring/loki",
            "monitoring/jaeger",
            "monitoring/opentelemetry",
        ],
    },
    {
        "id": "M16",
        "name": "Frontend dashboard",
        "area": "Frontend",
        "checks": [
            "frontend/package.json",
            "frontend/src",
        ],
    },
    {
        "id": "M17",
        "name": "System testing",
        "area": "Testing",
        "checks": [
            "tests/integration",
            "tests/e2e",
            "tests/pipeline",
            "tests/security",
            "tests/performance",
        ],
    },
    {
        "id": "M18",
        "name": "Learning/feedback engine",
        "area": "AI/ML",
        "checks": [
            "ai/learning/training",
            "ai/learning/feedback",
            "ai/learning/evaluation",
        ],
    },
    {
        "id": "M19",
        "name": "Documentation",
        "area": "Documentation",
        "checks": [
            "docs/architecture",
            "docs/api",
            "docs/ai",
            "docs/security",
            "docs/deployment",
            "docs/research",
            "docs/setup",
        ],
    },
]


def exists(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def is_nonempty_dir(path: Path) -> bool:
    return path.is_dir() and any(path.iterdir())


def check_status(root: Path, checks: list[str]) -> tuple[str, int, int]:
    """
    Returns:
        COMPLETE/PARTIAL/NOT_STARTED, passed_count, total_count
    """
    passed = sum(1 for c in checks if exists(root, c))
    total = len(checks)

    if passed == total:
        return "COMPLETE", passed, total
    if passed > 0:
        return "PARTIAL", passed, total
    return "NOT_STARTED", passed, total


def get_git_info(root: Path) -> dict:
    info = {
        "is_git_repo": (root / ".git").exists(),
        "branch": None,
        "commit_count": None,
        "last_commit": None,
        "status": None,
    }

    if not info["is_git_repo"]:
        return info

    def git(*args):
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    info["branch"] = git("branch", "--show-current")

    count = git("rev-list", "--count", "HEAD")
    if count and count.isdigit():
        info["commit_count"] = int(count)

    log = git("log", "-1", "--pretty=format:%h | %ad | %s", "--date=short")
    info["last_commit"] = log

    status = git("status", "--short")
    info["status"] = "clean" if status == "" else "changes present"

    return info


def build_tree(root: Path) -> str:
    lines = [f"{root.name}/"]

    def walk(directory: Path, prefix: str = ""):
        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            lines.append(prefix + "└── [permission denied]")
            return

        for index, entry in enumerate(entries):
            last = index == len(entries) - 1
            branch = "└── " if last else "├── "
            lines.append(prefix + branch + entry.name)

            if entry.is_dir():
                extension = "    " if last else "│   "
                walk(entry, prefix + extension)

    walk(root)
    return "\n".join(lines)


def count_project_files(root: Path) -> dict:
    files = 0
    dirs = 0

    for current, dirnames, filenames in os.walk(root):
        # Ignore generated/noisy directories when counting source progress.
        dirnames[:] = [
            d for d in dirnames
            if d not in {".git", "target", ".idea", "__pycache__", "node_modules"}
        ]
        dirs += len(dirnames)
        files += len(filenames)

    return {"source_directories": dirs, "source_files": files}


def calculate_progress(results: list[dict]) -> float:
    """
    Structural progress only.
    This intentionally does NOT claim that the project is functionally
    complete just because files/folders exist.
    """
    if not results:
        return 0.0

    weights = {
        "COMPLETE": 1.0,
        "PARTIAL": 0.5,
        "NOT_STARTED": 0.0,
    }

    return round(
        100 * sum(weights[r["status"]] for r in results) / len(results),
        1,
    )


def main():
    root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else DEFAULT_ROOT

    if not root.exists():
        print(f"ERROR: Project folder does not exist:\n{root}")
        print("\nRun with the correct path:")
        print(r'python sentinelai_progress_tracker.py "C:\path\to\11.SentiNelAI"')
        sys.exit(1)

    results = []

    for milestone in MILESTONES:
        status, passed, total = check_status(root, milestone["checks"])
        results.append({
            "id": milestone["id"],
            "name": milestone["name"],
            "area": milestone["area"],
            "status": status,
            "checks_passed": passed,
            "checks_total": total,
            "checks": milestone["checks"],
        })

    git_info = get_git_info(root)
    counts = count_project_files(root)
    structural_progress = calculate_progress(results)

    now = datetime.now().astimezone().isoformat(timespec="seconds")

    data = {
        "project": "SentinelAI",
        "generated_at": now,
        "project_root": str(root),
        "structural_progress_percent": structural_progress,
        "warning": (
            "This percentage is structural evidence only. "
            "A milestone must be functionally tested before calling it truly complete."
        ),
        "file_counts": counts,
        "git": git_info,
        "milestones": results,
        "tree_file": "SENTINELAI_TREE.txt",
    }

    # ---------------------------------------------------------------
    # Tree
    # ---------------------------------------------------------------
    tree = build_tree(root)
    (root / "SENTINELAI_TREE.txt").write_text(tree, encoding="utf-8")

    # ---------------------------------------------------------------
    # JSON
    # ---------------------------------------------------------------
    (root / "SENTINELAI_PROGRESS.json").write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # Markdown report
    # ---------------------------------------------------------------
    complete = sum(r["status"] == "COMPLETE" for r in results)
    partial = sum(r["status"] == "PARTIAL" for r in results)
    not_started = sum(r["status"] == "NOT_STARTED" for r in results)

    md = []
    md.append("# SentinelAI — Project Progress Report")
    md.append("")
    md.append(f"Generated: `{now}`")
    md.append(f"Project root: `{root}`")
    md.append("")
    md.append("> This report is intended to be shared with an AI assistant to understand the current project state.")
    md.append("> Structural checks are automatic; functional completion still requires tests/evidence.")
    md.append("")
    md.append("## Overall structural snapshot")
    md.append("")
    md.append(f"- Structural progress indicator: **{structural_progress}%**")
    md.append(f"- Milestones complete: **{complete}**")
    md.append(f"- Milestones partial: **{partial}**")
    md.append(f"- Milestones not started: **{not_started}**")
    md.append(f"- Source directories: **{counts['source_directories']}**")
    md.append(f"- Source files: **{counts['source_files']}**")
    md.append("")

    md.append("## Git")
    md.append("")
    md.append(f"- Git repository: **{'YES' if git_info['is_git_repo'] else 'NO'}**")
    md.append(f"- Branch: `{git_info['branch']}`")
    md.append(f"- Commit count: `{git_info['commit_count']}`")
    md.append(f"- Last commit: `{git_info['last_commit']}`")
    md.append(f"- Working tree: **{git_info['status']}**")
    md.append("")

    md.append("## Milestones")
    md.append("")
    md.append("| ID | Area | Milestone | Status | Evidence checks |")
    md.append("|---|---|---|---|---|")

    for r in results:
        icon = {
            "COMPLETE": "🟢",
            "PARTIAL": "🟡",
            "NOT_STARTED": "🔴",
        }[r["status"]]

        md.append(
            f"| {r['id']} | {r['area']} | {r['name']} | "
            f"{icon} **{r['status']}** | "
            f"{r['checks_passed']}/{r['checks_total']} |"
        )

    md.append("")
    md.append("## Exact evidence paths checked")
    md.append("")

    for r in results:
        md.append(f"### {r['id']} — {r['name']}")
        for check in r["checks"]:
            symbol = "✅" if exists(root, check) else "❌"
            md.append(f"- {symbol} `{check}`")
        md.append("")

    md.append("## Current project tree")
    md.append("")
    md.append("```text")
    md.append(tree)
    md.append("```")
    md.append("")

    md.append("## How to interpret this report")
    md.append("")
    md.append(
        "Use this file as a progress snapshot, not as proof that every existing "
        "file is correctly implemented. When a milestone is functionally tested, "
        "record that evidence in the project documentation/README and keep the "
        "relevant test files in the repository."
    )
    md.append("")

    (root / "SENTINELAI_PROGRESS.md").write_text(
        "\n".join(md),
        encoding="utf-8",
    )

    print("=" * 70)
    print("SentinelAI Progress Tracker")
    print("=" * 70)
    print(f"Project: {root}")
    print(f"Structural progress indicator: {structural_progress}%")
    print()
    for r in results:
        print(
            f"{r['id']} | {r['status']:<12} | "
            f"{r['name']} ({r['checks_passed']}/{r['checks_total']})"
        )

    print()
    print("Generated:")
    print(f"  {root / 'SENTINELAI_PROGRESS.md'}")
    print(f"  {root / 'SENTINELAI_PROGRESS.json'}")
    print(f"  {root / 'SENTINELAI_TREE.txt'}")
    print("=" * 70)


if __name__ == "__main__":
    main()