import tempfile
from pathlib import Path

from ai.dependency.extractor.dependency_extractor import (
    extract_repository_dependencies
)


def create_test_repository():

    temporary_directory = tempfile.TemporaryDirectory()

    repository = Path(
        temporary_directory.name
    )

    # ========================================================
    # main.py
    # ========================================================

    (repository / "main.py").write_text(
        """
import os
import helper
from utils import test_function
""",
        encoding="utf-8"
    )

    # ========================================================
    # helper.py
    # ========================================================

    (repository / "helper.py").write_text(
        """
def hello():
    return "hello"
""",
        encoding="utf-8"
    )

    # ========================================================
    # utils.py
    # ========================================================

    (repository / "utils.py").write_text(
        """
def test_function():
    return True
""",
        encoding="utf-8"
    )

    # ========================================================
    # Main.java
    # ========================================================

    (repository / "Main.java").write_text(
        """
import java.util.List;
import java.util.ArrayList;

public class Main {
}
""",
        encoding="utf-8"
    )

    # ========================================================
    # app.js
    # ========================================================

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

    print("=" * 60)
    print("PHASE 2 — DEPENDENCY EXTRACTOR TEST")
    print("=" * 60)

    temporary_directory, repository = (
        create_test_repository()
    )

    try:

        # ====================================================
        # TEST 1 — Repository scanning
        # ====================================================

        results = extract_repository_dependencies(
            repository
        )

        print("\nDetected dependency results:")

        for item in results:

            print(
                f"  {item['file']}: "
                f"{len(item['dependencies'])} dependencies"
            )

        # All five source files are returned by the
        # dependency extractor, including files having
        # zero dependencies.

        assert len(results) == 5

        print("[PASS] Repository scanning")

        # ====================================================
        # TEST 2 — Verify all expected files were scanned
        # ====================================================

        result_files = {
            item["file"]
            for item in results
        }

        expected_files = {
            "main.py",
            "helper.py",
            "utils.py",
            "Main.java",
            "app.js"
        }

        assert result_files == expected_files

        print("[PASS] All repository files detected")

        # ====================================================
        # TEST 3 — Python dependency extraction
        # ====================================================

        python_result = next(
            item for item in results
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

        # ====================================================
        # TEST 4 — Python files with no dependencies
        # ====================================================

        helper_result = next(
            item for item in results
            if item["file"] == "helper.py"
        )

        utils_result = next(
            item for item in results
            if item["file"] == "utils.py"
        )

        assert helper_result["dependencies"] == []
        assert utils_result["dependencies"] == []

        print("[PASS] Empty Python dependency detection")

        # ====================================================
        # TEST 5 — Java dependency extraction
        # ====================================================

        java_result = next(
            item for item in results
            if item["file"] == "Main.java"
        )

        java_dependencies = {
            item["name"]
            for item in java_result["dependencies"]
        }

        assert "java.util.List" in java_dependencies
        assert "java.util.ArrayList" in java_dependencies

        print("[PASS] Java dependency extraction")

        # ====================================================
        # TEST 6 — JavaScript dependency extraction
        # ====================================================

        js_result = next(
            item for item in results
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

        # ====================================================
        # FINAL RESULT
        # ====================================================

        print("=" * 60)
        print("ALL DEPENDENCY EXTRACTOR TESTS PASSED")
        print("=" * 60)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_tests()