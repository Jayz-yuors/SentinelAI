import tempfile

from pathlib import Path

from ai.dependency.dependency_pipeline import (
    analyze_dependencies
)

from ai.security.security_pipeline import (
    analyze_security_pipeline
)


def create_repository():

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    # ============================================================
    # DEPENDENCY TEST FILES
    # ============================================================

    (
        repository / "main.py"
    ).write_text(
        """
import helper
from utils import test_function

SECRET_KEY = "12345678901234567890"

user_input = input("Enter code: ")

result = eval(user_input)
""",
        encoding="utf-8"
    )

    (
        repository / "helper.py"
    ).write_text(
        """
def hello():
    return "hello"
""",
        encoding="utf-8"
    )

    (
        repository / "utils.py"
    ).write_text(
        """
def test_function():
    return True
""",
        encoding="utf-8"
    )

    # ============================================================
    # JAVA
    # ============================================================

    (
        repository / "Main.java"
    ).write_text(
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

    (
        repository / "app.js"
    ).write_text(
        """
import express from "express";
import helper from "./helper";
const fs = require("fs");
""",
        encoding="utf-8"
    )

    # ============================================================
    # VULNERABLE DEPENDENCY
    # ============================================================

    (
        repository / "requirements.txt"
    ).write_text(
        """
requests==1.0.0
flask==1.0.0
""",
        encoding="utf-8"
    )

    return temporary_directory, repository


def run_tests():

    print()
    print("=" * 80)
    print("SENTINELAI — COMPLETE PHASE 2 VALIDATION")
    print("=" * 80)

    temporary_directory, repository = (
        create_repository()
    )

    try:

        # ========================================================
        # DEPENDENCY INTELLIGENCE
        # ========================================================

        dependency_result = analyze_dependencies(
            repository
        )

        assert (
            dependency_result["success"] is True
        )

        print(
            "[PASS] TC01 — Dependency pipeline"
        )

        assert (
            "dependencyExtraction"
            in dependency_result
        )

        print(
            "[PASS] TC02 — Dependency extraction"
        )

        assert (
            len(
                dependency_result[
                    "dependencyGraph"
                ][
                    "nodes"
                ]
            ) > 0
        )

        print(
            "[PASS] TC03 — Dependency graph nodes"
        )

        assert (
            len(
                dependency_result[
                    "dependencyGraph"
                ][
                    "edges"
                ]
            ) > 0
        )

        print(
            "[PASS] TC04 — Dependency graph edges"
        )

        assert (
            "graphAnalysis"
            in dependency_result
        )

        print(
            "[PASS] TC05 — Graph analysis"
        )

        assert (
            "dependencyRisk"
            in dependency_result
        )

        print(
            "[PASS] TC06 — Dependency risk"
        )

        # ========================================================
        # SECURITY INTELLIGENCE
        # ========================================================

        security_result = (
            analyze_security_pipeline(
                repository
            )
        )

        assert (
            security_result["success"] is True
        )

        print(
            "[PASS] TC07 — Security pipeline"
        )

        assert (
            "secretAnalysis"
            in security_result
        )

        print(
            "[PASS] TC08 — Secret scanner"
        )

        assert (
            "vulnerabilityAnalysis"
            in security_result
        )

        print(
            "[PASS] TC09 — Vulnerability scanner"
        )

        assert (
            "cveAnalysis"
            in security_result
        )

        print(
            "[PASS] TC10 — CVE analysis"
        )

        assert (
            "staticAnalysis"
            in security_result
        )

        print(
            "[PASS] TC11 — Static security analysis"
        )

        assert (
            "threatAnalysis"
            in security_result
        )

        print(
            "[PASS] TC12 — Threat analysis"
        )

        assert (
            "securityTools"
            in security_result
        )

        print(
            "[PASS] TC13 — Security tool layer"
        )

        # ========================================================
        # CROSS-PIPELINE VALIDATION
        # ========================================================

        dependency_nodes = len(
            dependency_result[
                "dependencyGraph"
            ][
                "nodes"
            ]
        )

        dependency_edges = len(
            dependency_result[
                "dependencyGraph"
            ][
                "edges"
            ]
        )

        security_findings = (
            security_result[
                "threatAnalysis"
            ][
                "totalSecurityFindings"
            ]
        )

        threat_score = (
            security_result[
                "threatAnalysis"
            ][
                "threatScore"
            ]
        )

        assert dependency_nodes > 0

        assert dependency_edges > 0

        assert security_findings > 0

        assert threat_score > 0

        print(
            "[PASS] TC14 — Cross-analysis validation"
        )

        # ========================================================
        # SUMMARY
        # ========================================================

        print()
        print("-" * 80)

        print(
            "DEPENDENCY NODES:",
            dependency_nodes
        )

        print(
            "DEPENDENCY EDGES:",
            dependency_edges
        )

        print(
            "SECURITY FINDINGS:",
            security_findings
        )

        print(
            "THREAT SCORE:",
            threat_score
        )

        print(
            "THREAT LEVEL:",
            security_result[
                "threatAnalysis"
            ][
                "threatLevel"
            ]
        )

        print("-" * 80)

        print()
        print(
            "PHASE 2 VALIDATION SUCCESSFUL"
        )

        print(
            "ALL PHASE 2 CORE TEST CASES PASSED"
        )

        print()
        print("=" * 80)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_tests()