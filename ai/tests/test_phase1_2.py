import tempfile
import subprocess
from pathlib import Path

from ai.analyzer.repository.scanner import analyze_repository


# ============================================================
# TEST REPOSITORY
# ============================================================

def create_test_repository():

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    (repository / "main.py").write_text(
        """
import os
import helper
from utils import test_function

def main():
    return test_function()
""",
        encoding="utf-8"
    )

    (repository / "helper.py").write_text(
        """
def hello():
    return "hello"
""",
        encoding="utf-8"
    )

    (repository / "utils.py").write_text(
        """
def test_function():
    return True
""",
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Java
    # --------------------------------------------------------

    (repository / "Main.java").write_text(
        """
import java.util.List;
import java.util.ArrayList;

public class Main {
}
""",
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # JavaScript
    # --------------------------------------------------------

    (repository / "app.js").write_text(
        """
import express from "express";
import helper from "./helper";
const fs = require("fs");
""",
        encoding="utf-8"
    )

    return temporary_directory, repository


# ============================================================
# CREATE LOCAL GIT REPOSITORY
# ============================================================

def initialize_git_repository(repository):

    subprocess.run(
        ["git", "init"],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            "sentinelai@test.com"
        ],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.name",
            "SentinelAI Test"
        ],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True
    )

    subprocess.run(
        ["git", "add", "."],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Initial test commit"
        ],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True
    )


# ============================================================
# TESTS
# ============================================================

def run_tests():

    print()
    print("=" * 75)
    print("SENTINELAI — PHASE 1 + PHASE 2 INTEGRATION TEST")
    print("=" * 75)
    print()

    temporary_directory, repository = (
        create_test_repository()
    )

    try:

        # ----------------------------------------------------
        # Git setup
        # ----------------------------------------------------

        initialize_git_repository(
            repository
        )

        print(
            "[PASS] Test repository created"
        )

        # ----------------------------------------------------
        # Run integrated scanner
        # ----------------------------------------------------

        result = analyze_repository(
            repository.as_uri(),
            "master"
        )

        # ----------------------------------------------------
        # Overall execution
        # ----------------------------------------------------

        assert result["success"] is True

        print(
            "[PASS] Integrated repository analysis"
        )

        # ====================================================
        # PHASE 1 VALIDATION
        # ====================================================

        print()
        print("PHASE 1 VALIDATION")
        print("-" * 75)

        assert result["totalFiles"] >= 5

        print(
            "[PASS] Repository file collection"
        )

        assert "Python" in result["languages"]

        assert "Java" in result["languages"]

        assert "JavaScript" in result["languages"]

        print(
            "[PASS] Language detection"
        )

        assert result["fileTypes"]

        print(
            "[PASS] File type statistics"
        )

        assert isinstance(
            result["changedFiles"],
            list
        )

        print(
            "[PASS] Changed file analysis"
        )

        assert isinstance(
            result["codeStructure"],
            list
        )

        print(
            "[PASS] Code structure analysis"
        )

        assert isinstance(
            result["imports"],
            dict
        )

        print(
            "[PASS] Import analysis"
        )

        assert (
            "impactAnalysis"
            in result
        )

        print(
            "[PASS] Change impact analysis"
        )

        # ====================================================
        # PHASE 2 VALIDATION
        # ====================================================

        print()
        print("PHASE 2 VALIDATION")
        print("-" * 75)

        dependency_extraction = (
            result["dependencyExtraction"]
        )

        assert len(
            dependency_extraction
        ) == 5

        print(
            "[PASS] Dependency extraction"
        )

        dependency_graph = (
            result["dependencyGraph"]
        )

        assert len(
            dependency_graph["nodes"]
        ) > 0

        print(
            "[PASS] Dependency graph nodes"
        )

        assert len(
            dependency_graph["edges"]
        ) > 0

        print(
            "[PASS] Dependency graph edges"
        )

        graph_analysis = (
            result["graphAnalysis"]
        )

        assert (
            "totalNodes"
            in graph_analysis
        )

        assert (
            "totalEdges"
            in graph_analysis
        )

        assert (
            "dependencyCounts"
            in graph_analysis
        )

        print(
            "[PASS] Graph analysis"
        )

        dependency_risk = (
            result["dependencyRisk"]
        )

        assert (
            "overallScore"
            in dependency_risk
        )

        assert (
            "overallRisk"
            in dependency_risk
        )

        assert (
            "fileRisks"
            in dependency_risk
        )

        print(
            "[PASS] Dependency risk analysis"
        )

        # ====================================================
        # CROSS-PHASE VALIDATION
        # ====================================================

        print()
        print("CROSS-PHASE VALIDATION")
        print("-" * 75)

        assert (
            result["repositoryName"]
            == repository.name
        )

        print(
            "[PASS] Shared repository analysis context"
        )

        assert (
            result["totalFiles"]
            > 0
        )

        assert (
            len(dependency_graph["nodes"])
            > 0
        )

        print(
            "[PASS] Phase 1 + Phase 2 data coexistence"
        )

        # ====================================================
        # SUMMARY
        # ====================================================

        print()
        print("=" * 75)
        print("PHASE 1 + PHASE 2 INTEGRATION SUCCESSFUL")
        print("=" * 75)

        print()
        print(
            "Repository Files:",
            result["totalFiles"]
        )

        print(
            "Languages:",
            ", ".join(result["languages"])
        )

        print(
            "Dependency Nodes:",
            graph_analysis["totalNodes"]
        )

        print(
            "Dependency Edges:",
            graph_analysis["totalEdges"]
        )

        print(
            "Dependency Risk:",
            dependency_risk["overallRisk"]
        )

        print(
            "Risk Score:",
            dependency_risk["overallScore"]
        )

        print()
        print(
            "PHASE 1 + PHASE 2 TEST PASSED"
        )
        print("=" * 75)

    finally:

        temporary_directory.cleanup()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_tests()