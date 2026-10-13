import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict


DEFAULT_TIMEOUT = int(
    os.getenv("SENTINELAI_SECURITY_TOOL_TIMEOUT", "300")
)


def _find_command(*commands: str) -> str | None:

    for command in commands:
        path = shutil.which(command)

        if path:
            return path

    return None


def _run_command(
    command: list[str],
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:

    try:

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )

        return {
            "success": completed.returncode == 0,
            "exitCode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    except subprocess.TimeoutExpired as exc:

        return {
            "success": False,
            "exitCode": None,
            "stdout": exc.stdout or "",
            "stderr": "External security tool timed out.",
            "timeout": True,
        }

    except Exception as exc:

        return {
            "success": False,
            "exitCode": None,
            "stdout": "",
            "stderr": str(exc),
            "timeout": False,
        }


def _read_json(path: Path) -> Any:

    if not path.exists():
        return {}

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def _parse_gitleaks(path: Path) -> Dict[str, Any]:

    data = _read_json(path)

    findings = data if isinstance(data, list) else []

    return {
        "findingCount": len(findings),
        "findings": findings,
    }


def _parse_trivy(path: Path) -> Dict[str, Any]:

    data = _read_json(path)

    findings = []

    for result in data.get("Results", []):

        vulnerabilities = result.get(
            "Vulnerabilities",
            []
        )

        if vulnerabilities:

            findings.extend(vulnerabilities)

    return {
        "findingCount": len(findings),
        "findings": findings,
    }


def _parse_semgrep(path: Path) -> Dict[str, Any]:

    data = _read_json(path)

    findings = data.get(
        "results",
        []
    )

    return {
        "findingCount": len(findings),
        "findings": findings,
    }


def _parse_dependency_check(
    path: Path
) -> Dict[str, Any]:

    data = _read_json(path)

    findings = []

    for dependency in data.get(
        "dependencies",
        []
    ):

        vulnerabilities = dependency.get(
            "vulnerabilities",
            []
        )

        findings.extend(vulnerabilities)

    return {
        "findingCount": len(findings),
        "findings": findings,
    }


def run_external_security_tools(
    repository_path: str | Path
) -> Dict[str, Any]:

    repository_path = Path(repository_path)

    if not repository_path.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {repository_path}"
        )

    enabled = os.getenv(
        "SENTINELAI_EXTERNAL_TOOLS_ENABLED",
        "false"
    ).lower() == "true"

    if not enabled:

        return {
            "enabled": False,
            "success": True,
            "tools": {},
            "message": "External security tools disabled."
        }

    result: Dict[str, Any] = {
        "enabled": True,
        "success": True,
        "tools": {},
    }

    with tempfile.TemporaryDirectory(
        prefix="sentinelai_security_"
    ) as temp_directory:

        temp_path = Path(temp_directory)

        # ---------------------------------------------
        # GITLEAKS
        # ---------------------------------------------

        gitleaks = _find_command(
            "gitleaks"
        )

        if gitleaks:

            report = (
                temp_path /
                "gitleaks.json"
            )

            execution = _run_command([
                gitleaks,
                "detect",
                "--source",
                str(repository_path),
                "--report-format",
                "json",
                "--report-path",
                str(report),
                "--no-banner",
            ])

            parsed = _parse_gitleaks(
                report
            )

            result["tools"]["gitleaks"] = {
                **execution,
                **parsed,
            }

        else:

            result["tools"]["gitleaks"] = {
                "available": False,
                "success": False,
                "findingCount": 0,
                "findings": [],
                "error": "gitleaks not found on PATH.",
            }

        # ---------------------------------------------
        # TRIVY
        # ---------------------------------------------

        trivy = _find_command(
            "trivy"
        )

        if trivy:

            report = (
                temp_path /
                "trivy.json"
            )

            execution = _run_command([
                trivy,
                "fs",
                "--format",
                "json",
                "--output",
                str(report),
                str(repository_path),
            ])

            parsed = _parse_trivy(
                report
            )

            result["tools"]["trivy"] = {
                **execution,
                **parsed,
            }

        else:

            result["tools"]["trivy"] = {
                "available": False,
                "success": False,
                "findingCount": 0,
                "findings": [],
                "error": "trivy not found on PATH.",
            }

        # ---------------------------------------------
        # SEMGREP
        # ---------------------------------------------

        semgrep = _find_command(
            "semgrep"
        )

        if semgrep:

            report = (
                temp_path /
                "semgrep.json"
            )

            execution = _run_command([
                semgrep,
                "--config",
                "auto",
                "--json",
                "--output",
                str(report),
                str(repository_path),
            ])

            parsed = _parse_semgrep(
                report
            )

            result["tools"]["semgrep"] = {
                **execution,
                **parsed,
            }

        else:

            result["tools"]["semgrep"] = {
                "available": False,
                "success": False,
                "findingCount": 0,
                "findings": [],
                "error": "semgrep not found on PATH.",
            }

        # ---------------------------------------------
        # OWASP DEPENDENCY-CHECK
        # ---------------------------------------------

        dependency_check = _find_command(
            "dependency-check.bat",
            "dependency-check",
            "dependency-check.sh",
        )

        if dependency_check:

            output_directory = (
                temp_path /
                "dependency-check"
            )

            output_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            execution = _run_command([
                dependency_check,
                "--project",
                "SentinelAI",
                "--scan",
                str(repository_path),
                "--format",
                "JSON",
                "--out",
                str(output_directory),
            ])

            report = (
                output_directory /
                "dependency-check-report.json"
            )

            parsed = (
                _parse_dependency_check(
                    report
                )
            )

            result["tools"][
                "dependency-check"
            ] = {
                **execution,
                **parsed,
            }

        else:

            result["tools"][
                "dependency-check"
            ] = {
                "available": False,
                "success": False,
                "findingCount": 0,
                "findings": [],
                "error": (
                    "dependency-check not "
                    "found on PATH."
                ),
            }

        # ---------------------------------------------
        # SONARQUBE / SONARSCANNER
        # ---------------------------------------------

        sonar_scanner = _find_command(
            "sonar-scanner.bat",
            "sonar-scanner",
        )

        if sonar_scanner:

            sonar_host = os.getenv(
                "SONAR_HOST_URL",
                "http://localhost:9000"
            )

            sonar_token = os.getenv(
                "SONAR_TOKEN",
                ""
            )

            command = [
                sonar_scanner,
                f"-Dsonar.projectKey=sentinelai-analysis",
                f"-Dsonar.projectName=SentinelAI",
                f"-Dsonar.sources={repository_path}",
                f"-Dsonar.host.url={sonar_host}",
            ]

            if sonar_token:

                command.append(
                    f"-Dsonar.token={sonar_token}"
                )

            execution = _run_command(
                command
            )

            result["tools"]["sonarqube"] = {
                **execution,
                "findingCount": 0,
                "findings": [],
                "message": (
                    "SonarScanner execution "
                    "completed. Detailed "
                    "quality-gate retrieval "
                    "can be added after "
                    "server integration."
                ),
            }

        else:

            result["tools"]["sonarqube"] = {
                "available": False,
                "success": False,
                "findingCount": 0,
                "findings": [],
                "error": (
                    "sonar-scanner not "
                    "found on PATH."
                ),
            }

    # ---------------------------------------------
    # OVERALL RESULT
    # ---------------------------------------------

    failures = []

    for tool_name, tool_result in (
        result["tools"].items()
    ):

        if not tool_result.get(
            "success",
            False
        ):

            failures.append(
                tool_name
            )

    result["failedTools"] = failures

    # A tool being unavailable is not silently
    # converted into a successful scan.
    result["success"] = (
        len(failures) == 0
    )

    return result