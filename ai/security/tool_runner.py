import json
import shutil
import subprocess
from pathlib import Path


def is_tool_available(
    tool_name: str
):

    return shutil.which(
        tool_name
    ) is not None


def run_tool(
    command: list[str],
    repository_path: Path
):

    try:

        result = subprocess.run(
            command,
            cwd=repository_path,
            capture_output=True,
            text=True,
            timeout=300
        )

        return {
            "available": True,
            "returnCode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:

        return {
            "available": True,
            "returnCode": -1,
            "stdout": "",
            "stderr": "Tool execution timed out"
        }

    except OSError as error:

        return {
            "available": False,
            "returnCode": -1,
            "stdout": "",
            "stderr": str(error)
        }


def run_gitleaks(
    repository_path: Path
):

    if not is_tool_available("gitleaks"):

        return {
            "tool": "gitleaks",
            "available": False,
            "message": "Gitleaks is not installed"
        }

    return run_tool(
        [
            "gitleaks",
            "detect",
            "--source",
            ".",
            "--report-format",
            "json",
            "--report-path",
            "gitleaks-report.json"
        ],
        repository_path
    )


def run_semgrep(
    repository_path: Path
):

    if not is_tool_available("semgrep"):

        return {
            "tool": "semgrep",
            "available": False,
            "message": "Semgrep is not installed"
        }

    return run_tool(
        [
            "semgrep",
            "--config",
            "auto",
            "--json"
        ],
        repository_path
    )


def run_trivy(
    repository_path: Path
):

    if not is_tool_available("trivy"):

        return {
            "tool": "trivy",
            "available": False,
            "message": "Trivy is not installed"
        }

    return run_tool(
        [
            "trivy",
            "fs",
            "--format",
            "json",
            "."
        ],
        repository_path
    )


def run_security_tools(
    repository_path: Path
):

    return {
        "gitleaks": run_gitleaks(
            repository_path
        ),

        "semgrep": run_semgrep(
            repository_path
        ),

        "trivy": run_trivy(
            repository_path
        )
    }