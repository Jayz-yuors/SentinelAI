import subprocess
import tempfile
from pathlib import Path

from ai.analyzer.repository.scanner import (
    analyze_repository
)


# ============================================================
# HELPER — RUN COMMAND
# ============================================================

def run_command(
    command,
    cwd
):

    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"Command failed:\n"
            f"{' '.join(command)}\n\n"
            f"{result.stderr}"
        )

    return result


# ============================================================
# CREATE TEST REPOSITORY
# ============================================================

def create_test_repository(
    repository_path: Path
):

    repository_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Initialize Git repository
    # --------------------------------------------------------

    run_command(
        [
            "git",
            "init",
            "-b",
            "main"
        ],
        repository_path
    )

    # --------------------------------------------------------
    # Git identity
    # --------------------------------------------------------

    run_command(
        [
            "git",
            "config",
            "user.email",
            "sentinelai@test.com"
        ],
        repository_path
    )

    run_command(
        [
            "git",
            "config",
            "user.name",
            "SentinelAI Test"
        ],
        repository_path
    )

    # --------------------------------------------------------
    # Application file
    # --------------------------------------------------------

    app_file = (
        repository_path
        / "app.py"
    )

    app_file.write_text(
        '''
import os

API_KEY = "ABCDEF12345678901234"
PASSWORD = "supersecret123"

def execute_user_input(user_input):
    return eval(user_input)

print("SentinelAI integration test")
''',
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Dependency file
    # --------------------------------------------------------

    requirements_file = (
        repository_path
        / "requirements.txt"
    )

    requirements_file.write_text(
        """
requests==2.31.0
flask==2.2.5
""",
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # README
    # --------------------------------------------------------

    readme_file = (
        repository_path
        / "README.md"
    )

    readme_file.write_text(
        "# SentinelAI Phase 1 + 2 + 3 Integration Test",
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # First commit
    # --------------------------------------------------------

    run_command(
        [
            "git",
            "add",
            "."
        ],
        repository_path
    )

    run_command(
        [
            "git",
            "commit",
            "-m",
            "Initial commit"
        ],
        repository_path
    )

    # --------------------------------------------------------
    # Make a second commit
    #
    # This allows Phase 1 change-impact analysis to operate.
    # --------------------------------------------------------

    app_file.write_text(
        '''
import os

API_KEY = "ABCDEF12345678901234"
PASSWORD = "supersecret123"

def execute_user_input(user_input):
    return eval(user_input)

def sentinelai_test():
    return "updated"

print("SentinelAI integration test")
''',
        encoding="utf-8"
    )

    run_command(
        [
            "git",
            "add",
            "."
        ],
        repository_path
    )

    run_command(
        [
            "git",
            "commit",
            "-m",
            "Update application"
        ],
        repository_path
    )


# ============================================================
# MAIN TEST
# ============================================================

def run_test():

    print()
    print("=" * 75)
    print(
        "SENTINELAI — PHASE 1 + PHASE 2 + PHASE 3 "
        "INTEGRATION TEST"
    )
    print("=" * 75)

    with tempfile.TemporaryDirectory() as temp:

        temp_path = Path(temp)

        source_repository = (
            temp_path
            / "sentinelai_test_repo"
        )

        # ----------------------------------------------------
        # Create test repository
        # ----------------------------------------------------

        create_test_repository(
            source_repository
        )

        print(
            "[PASS] Test repository created"
        )

        # ----------------------------------------------------
        # Execute complete integrated analysis
        # ----------------------------------------------------

        result = analyze_repository(
            str(source_repository),
            "main"
        )

        # ====================================================
        # BASIC VALIDATION
        # ====================================================

        assert result["success"] is True

        print(
            "[PASS] Integrated repository analysis"
        )

        # ====================================================
        # PHASE 1 VALIDATION
        # ====================================================

        assert result["totalFiles"] >= 3

        print(
            "[PASS] Phase 1 — Repository file collection"
        )

        assert len(
            result["languages"]
        ) >= 1

        print(
            "[PASS] Phase 1 — Language detection"
        )

        assert len(
            result["fileTypes"]
        ) >= 1

        print(
            "[PASS] Phase 1 — File type statistics"
        )

        assert isinstance(
            result["changedFiles"],
            list
        )

        print(
            "[PASS] Phase 1 — Changed file analysis"
        )

        assert isinstance(
            result["codeStructure"],
            list
        )

        print(
            "[PASS] Phase 1 — Code structure analysis"
        )

        assert isinstance(
            result["imports"],
            dict
        )

        print(
            "[PASS] Phase 1 — Import analysis"
        )

        assert isinstance(
            result["impactAnalysis"],
            dict
        )

        print(
            "[PASS] Phase 1 — Change impact analysis"
        )

        # ====================================================
        # PHASE 2 VALIDATION
        # ====================================================

        assert isinstance(
            result["dependencyExtraction"],
            list
        )

        print(
            "[PASS] Phase 2 — Dependency extraction"
        )

        dependency_graph = (
            result["dependencyGraph"]
        )

        assert "nodes" in dependency_graph
        assert "edges" in dependency_graph

        print(
            "[PASS] Phase 2 — Dependency graph"
        )

        graph_analysis = (
            result["graphAnalysis"]
        )

        assert isinstance(
            graph_analysis,
            dict
        )

        print(
            "[PASS] Phase 2 — Graph analysis"
        )

        dependency_risk = (
            result["dependencyRisk"]
        )

        assert isinstance(
            dependency_risk,
            dict
        )

        print(
            "[PASS] Phase 2 — Dependency risk analysis"
        )

        # ====================================================
        # PHASE 3 VALIDATION
        # ====================================================

        security_analysis = (
            result["securityAnalysis"]
        )

        assert isinstance(
            security_analysis,
            dict
        )

        print(
            "[PASS] Phase 3 — Security analysis"
        )

        assert "secrets" in security_analysis

        print(
            "[PASS] Phase 3 — Secret analysis"
        )

        assert "dependencyVulnerabilities" in security_analysis

        print(
            "[PASS] Phase 3 — Vulnerability analysis"
        )

        assert "cves" in security_analysis

        print(
            "[PASS] Phase 3 — CVE analysis"
        )

        assert "staticAnalysis" in security_analysis

        print(
            "[PASS] Phase 3 — Static security analysis"
        )

        assert "threatAnalysis" in security_analysis

        print(
            "[PASS] Phase 3 — Threat analysis"
        )

        assert "risk" in security_analysis

        print(
            "[PASS] Phase 3 — Security risk scoring"
        )

        assert isinstance(
            security_analysis["findings"],
            list
        )

        print(
            "[PASS] Phase 3 — Unified security findings"
        )

        # ====================================================
        # CROSS-PHASE VALIDATION
        # ====================================================

        assert (
            "dependencyContext"
            in security_analysis
        )

        print(
            "[PASS] Phase 2 → Phase 3 dependency context"
        )

        assert (
            security_analysis["dependencyContext"]
            is not None
        )

        print(
            "[PASS] Shared Phase 2 → Phase 3 analysis context"
        )

        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        findings = (
            security_analysis["findings"]
        )

        risk = (
            security_analysis["risk"]
        )

        print()
        print("-" * 75)

        print(
            f"REPOSITORY FILES: "
            f"{result['totalFiles']}"
        )

        print(
            f"LANGUAGES: "
            f"{', '.join(result['languages'])}"
        )

        print(
            f"DEPENDENCY NODES: "
            f"{len(dependency_graph['nodes'])}"
        )

        print(
            f"DEPENDENCY EDGES: "
            f"{len(dependency_graph['edges'])}"
        )

        print(
            f"SECURITY FINDINGS: "
            f"{len(findings)}"
        )

        print(
            f"SECURITY RISK: "
            f"{risk.get('overallRisk', 'UNKNOWN')}"
        )

        print(
            f"SECURITY RISK SCORE: "
            f"{risk.get('overallScore', 0)}"
        )

        print("-" * 75)

        print()
        print(
            "PHASE 1 + PHASE 2 + PHASE 3 "
            "INTEGRATION SUCCESSFUL"
        )

        print(
            "ALL PHASE 1 + PHASE 2 + PHASE 3 "
            "TESTS PASSED"
        )

        print("=" * 75)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_test()