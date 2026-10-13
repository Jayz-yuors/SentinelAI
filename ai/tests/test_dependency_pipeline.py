import tempfile
from pathlib import Path

from ai.dependency.dependency_pipeline import (
    analyze_dependencies
)


def create_test_repository():

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    # ============================================================
    # PYTHON FILES
    # ============================================================

    (repository / "main.py").write_text(
        """
import os
import helper
from utils import test_function
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

    # ============================================================
    # JAVA
    # ============================================================

    (repository / "Main.java").write_text(
        """
import java.util.List;
import java.util.ArrayList;

public class Main {
}
""",
        encoding="utf-8"
    )

    # ============================================================
    # JAVASCRIPT
    # ============================================================

    (repository / "app.js").write_text(
        """
import express from "express";
import helper from "./helper";
const fs = require("fs");
""",
        encoding="utf-8"
    )

    return temporary_directory, repository


def run_tests():

    print("=" * 70)
    print("PHASE 2 — COMPLETE DEPENDENCY PIPELINE TEST")
    print("=" * 70)

    temporary_directory, repository = (
        create_test_repository()
    )

    try:

        # ========================================================
        # TEST 1 — PIPELINE EXECUTION
        # ========================================================

        result = analyze_dependencies(
            repository
        )

        assert result["success"] is True

        print("[PASS] Pipeline execution")

        # ========================================================
        # TEST 2 — DEPENDENCY EXTRACTION
        # ========================================================

        dependency_extraction = result[
            "dependencyExtraction"
        ]

        # Five source files exist in the test repository:
        #
        # main.py
        # helper.py
        # utils.py
        # Main.java
        # app.js

        assert len(
            dependency_extraction
        ) == 5

        print("[PASS] Dependency extraction")

        # ========================================================
        # TEST 3 — VERIFY ALL FILES WERE EXTRACTED
        # ========================================================

        extracted_files = {
            item["file"]
            for item in dependency_extraction
        }

        expected_files = {
            "main.py",
            "helper.py",
            "utils.py",
            "Main.java",
            "app.js"
        }

        assert extracted_files == expected_files

        print("[PASS] All repository files detected")

        # ========================================================
        # TEST 4 — VERIFY PYTHON DEPENDENCIES
        # ========================================================

        python_result = next(
            item
            for item in dependency_extraction
            if item["file"] == "main.py"
        )

        python_dependencies = {
            item["name"]
            for item in python_result["dependencies"]
        }

        assert "os" in python_dependencies
        assert "helper" in python_dependencies
        assert "utils" in python_dependencies

        print("[PASS] Python dependency extraction")

        # ========================================================
        # TEST 5 — VERIFY EMPTY PYTHON FILE DEPENDENCIES
        # ========================================================

        helper_result = next(
            item
            for item in dependency_extraction
            if item["file"] == "helper.py"
        )

        assert (
            helper_result["dependencies"] == []
        )

        utils_result = next(
            item
            for item in dependency_extraction
            if item["file"] == "utils.py"
        )

        assert (
            utils_result["dependencies"] == []
        )

        print("[PASS] Empty Python dependency detection")

        # ========================================================
        # TEST 6 — VERIFY JAVA DEPENDENCIES
        # ========================================================

        java_result = next(
            item
            for item in dependency_extraction
            if item["file"] == "Main.java"
        )

        java_dependencies = {
            item["name"]
            for item in java_result["dependencies"]
        }

        assert "java.util.List" in java_dependencies
        assert "java.util.ArrayList" in java_dependencies

        print("[PASS] Java dependency extraction")

        # ========================================================
        # TEST 7 — VERIFY JAVASCRIPT DEPENDENCIES
        # ========================================================

        js_result = next(
            item
            for item in dependency_extraction
            if item["file"] == "app.js"
        )

        js_dependencies = {
            item["name"]
            for item in js_result["dependencies"]
        }

        assert "express" in js_dependencies
        assert "./helper" in js_dependencies
        assert "fs" in js_dependencies

        print("[PASS] JavaScript dependency extraction")

        # ========================================================
        # TEST 8 — GRAPH CREATION
        # ========================================================

        graph = result[
            "dependencyGraph"
        ]

        assert len(
            graph["nodes"]
        ) > 0

        print("[PASS] Graph node creation")

        assert len(
            graph["edges"]
        ) > 0

        print("[PASS] Graph edge creation")

        # ========================================================
        # TEST 9 — GRAPH ANALYSIS
        # ========================================================

        analysis = result[
            "graphAnalysis"
        ]

        assert "totalNodes" in analysis
        assert "totalEdges" in analysis
        assert "dependencyCounts" in analysis
        assert "highImpactFiles" in analysis
        assert "circularDependencies" in analysis

        print("[PASS] Graph analysis")

        # ========================================================
        # TEST 10 — DEPENDENCY RISK
        # ========================================================

        risk = result[
            "dependencyRisk"
        ]

        assert "overallScore" in risk
        assert "overallRisk" in risk
        assert "fileRisks" in risk

        print("[PASS] Dependency risk analysis")

        # ========================================================
        # FINAL SUMMARY
        # ========================================================

        print()
        print(
            "Nodes:",
            analysis["totalNodes"]
        )

        print(
            "Edges:",
            analysis["totalEdges"]
        )

        print(
            "Overall Risk:",
            risk["overallRisk"]
        )

        print(
            "Risk Score:",
            risk["overallScore"]
        )

        print()
        print("=" * 70)
        print("ALL DEPENDENCY PIPELINE TESTS PASSED")
        print("=" * 70)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_tests()