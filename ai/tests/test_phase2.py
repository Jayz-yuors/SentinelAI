import tempfile
from pathlib import Path

from ai.dependency.extractor.dependency_extractor import (
    extract_repository_dependencies
)

from ai.dependency.graph.dependency_graph import (
    build_dependency_graph
)

from ai.dependency.graph.graph_analyzer import (
    analyze_graph
)

from ai.dependency.graph.dependency_risk import (
    calculate_dependency_risk
)

from ai.dependency.dependency_pipeline import (
    analyze_dependencies
)


# ============================================================
# TEST REPOSITORY
# ============================================================

def create_test_repository():

    temp = tempfile.TemporaryDirectory()

    repository = Path(
        temp.name
    )

    # -----------------------------
    # Python
    # -----------------------------

    (repository / "main.py").write_text(
        """
import os
import helper
from utils import calculate
""",
        encoding="utf-8"
    )

    (repository / "helper.py").write_text(
        """
from utils import calculate

def run():
    return calculate()
""",
        encoding="utf-8"
    )

    (repository / "utils.py").write_text(
        """
def calculate():
    return 100
""",
        encoding="utf-8"
    )

    # -----------------------------
    # Java
    # -----------------------------

    (repository / "Main.java").write_text(
        """
import java.util.List;
import java.util.ArrayList;

public class Main {

    public static void main(String[] args) {

        List<String> values =
            new ArrayList<>();

    }
}
""",
        encoding="utf-8"
    )

    # -----------------------------
    # JavaScript
    # -----------------------------

    (repository / "app.js").write_text(
        """
import express from "express";
import helper from "./helper";
const fs = require("fs");
""",
        encoding="utf-8"
    )

    return temp, repository


# ============================================================
# TEST 1 — EXTRACTION
# ============================================================

def test_extraction(repository):

    results = extract_repository_dependencies(
        repository
    )

    assert len(results) == 5

    print(
        "[PASS] TC01 — Repository dependency extraction"
    )

    return results


# ============================================================
# TEST 2 — GRAPH
# ============================================================

def test_graph(results):

    graph = build_dependency_graph(
        results
    )

    assert len(
        graph.nodes
    ) > 0

    print(
        "[PASS] TC02 — Graph nodes generated"
    )

    assert len(
        graph.edges
    ) > 0

    print(
        "[PASS] TC03 — Graph edges generated"
    )

    return graph


# ============================================================
# TEST 3 — INTERNAL DEPENDENCY
# ============================================================

def test_internal_dependency(graph):

    dependencies = (
        graph.get_dependencies(
            "main.py"
        )
    )

    assert "helper.py" in dependencies

    print(
        "[PASS] TC04 — Internal dependency detected"
    )


# ============================================================
# TEST 4 — REVERSE DEPENDENCY
# ============================================================

def test_reverse_dependency(graph):

    dependents = (
        graph.get_dependents(
            "utils.py"
        )
    )

    assert "main.py" in dependents

    assert "helper.py" in dependents

    print(
        "[PASS] TC05 — Reverse dependency lookup"
    )


# ============================================================
# TEST 5 — GRAPH ANALYSIS
# ============================================================

def test_graph_analysis(graph):

    analysis = analyze_graph(
        graph
    )

    assert analysis[
        "totalNodes"
    ] > 0

    assert analysis[
        "totalEdges"
    ] > 0

    print(
        "[PASS] TC06 — Graph analysis"
    )

    assert isinstance(
        analysis[
            "dependencyCounts"
        ],
        dict
    )

    print(
        "[PASS] TC07 — Dependency counts"
    )

    return analysis


# ============================================================
# TEST 6 — CYCLE DETECTION
# ============================================================

def test_cycle_detection(graph):

    analysis = analyze_graph(
        graph
    )

    assert isinstance(
        analysis[
            "circularDependencies"
        ],
        list
    )

    print(
        "[PASS] TC08 — Circular dependency analysis"
    )


# ============================================================
# TEST 7 — ISOLATED NODES
# ============================================================

def test_isolated_nodes(graph):

    analysis = analyze_graph(
        graph
    )

    assert isinstance(
        analysis[
            "isolatedNodes"
        ],
        list
    )

    print(
        "[PASS] TC09 — Isolated node detection"
    )


# ============================================================
# TEST 8 — RISK ANALYSIS
# ============================================================

def test_risk(graph):

    risk = calculate_dependency_risk(
        graph
    )

    assert "overallScore" in risk

    assert "overallRisk" in risk

    assert "fileRisks" in risk

    print(
        "[PASS] TC10 — Dependency risk calculation"
    )

    return risk


# ============================================================
# TEST 9 — COMPLETE PIPELINE
# ============================================================

def test_complete_pipeline(repository):

    result = analyze_dependencies(
        repository
    )

    assert result["success"] is True

    assert (
        "dependencyExtraction"
        in result
    )

    assert (
        "dependencyGraph"
        in result
    )

    assert (
        "graphAnalysis"
        in result
    )

    assert (
        "dependencyRisk"
        in result
    )

    print(
        "[PASS] TC11 — Complete Phase 2 pipeline"
    )

    return result


# ============================================================
# MAIN TEST RUNNER
# ============================================================

def main():

    print()
    print("=" * 75)
    print("SENTINELAI — PHASE 2 VALIDATION")
    print("=" * 75)
    print()

    temporary_directory, repository = (
        create_test_repository()
    )

    try:

        results = test_extraction(
            repository
        )

        graph = test_graph(
            results
        )

        test_internal_dependency(
            graph
        )

        test_reverse_dependency(
            graph
        )

        test_graph_analysis(
            graph
        )

        test_cycle_detection(
            graph
        )

        test_isolated_nodes(
            graph
        )

        test_risk(
            graph
        )

        final_result = test_complete_pipeline(
            repository
        )

        print()
        print("-" * 75)

        print(
            "TOTAL NODES:",
            final_result[
                "graphAnalysis"
            ][
                "totalNodes"
            ]
        )

        print(
            "TOTAL EDGES:",
            final_result[
                "graphAnalysis"
            ][
                "totalEdges"
            ]
        )

        print(
            "OVERALL RISK:",
            final_result[
                "dependencyRisk"
            ][
                "overallRisk"
            ]
        )

        print(
            "RISK SCORE:",
            final_result[
                "dependencyRisk"
            ][
                "overallScore"
            ]
        )

        print("-" * 75)

        print()
        print(
            "PHASE 2 VALIDATION SUCCESSFUL"
        )
        print(
            "ALL TEST CASES PASSED"
        )

        print()
        print("=" * 75)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    main()