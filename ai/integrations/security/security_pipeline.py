from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai.integrations.security.security_runtime import SecurityToolRuntime
from ai.integrations.security.tool_registry import get_security_tools

from ai.integrations.security.parsers import (
    GitleaksParser,
    TrivyParser,
    SemgrepParser,
    DependencyCheckParser,
    SonarParser,
)

from ai.intelligence.risk.risk_engine import UnifiedRiskEngine


@dataclass
class SecurityPipelineResult:
    findings: list[Any] = field(default_factory=list)
    risk_profile: Any = None
    tool_results: dict[str, Any] = field(default_factory=dict)


class SecurityPipeline:

    def __init__(self):
        self.runtime = SecurityToolRuntime()
        self.tools = get_security_tools()

        self.parsers = {
            "gitleaks": GitleaksParser(),
            "trivy": TrivyParser(),
            "semgrep": SemgrepParser(),
            "dependency-check": DependencyCheckParser(),
            "sonar": SonarParser(),
        }

    def parse_output(
        self,
        tool_name: str,
        raw_output: str,
    ) -> list[Any]:

        parser = self.parsers.get(tool_name)

        if parser is None:
            raise ValueError(
                f"No parser registered for tool: {tool_name}"
            )

        return parser.parse(raw_output)

    def combine_findings(
        self,
        findings: list[Any],
    ) -> Any:

        engine = UnifiedRiskEngine()

        return engine.analyze(findings)

    def run_gitleaks(
        self,
        repository_path: str,
    ) -> tuple[Any, list[Any]]:

        config = self.tools["gitleaks"]

        output_file = (
            Path(repository_path)
            / ".sentinelai-gitleaks.json"
        )

        args = [
            "detect",
            "--source",
            repository_path,
            "--report-format",
            "json",
            "--report-path",
            str(output_file),
            "--no-banner",
        ]

        result = self.runtime.execute(
            config=config,
            args=args,
            cwd=repository_path,
        )

        raw_output = ""

        if output_file.exists():
            raw_output = output_file.read_text(
                encoding="utf-8",
                errors="replace",
            )

            try:
                output_file.unlink()
            except OSError:
                pass

        findings = self.parse_output(
            "gitleaks",
            raw_output,
        )

        return result, findings

    def run_trivy(
        self,
        repository_path: str,
    ) -> tuple[Any, list[Any]]:

        config = self.tools["trivy"]

        args = [
            "fs",
            "--format",
            "json",
            "--scanners",
            "vuln,misconfig,secret",
            repository_path,
        ]

        result = self.runtime.execute(
            config=config,
            args=args,
            cwd=repository_path,
        )

        findings = self.parse_output(
            "trivy",
            result.stdout,
        )

        return result, findings

    def run_semgrep(
        self,
        repository_path: str,
    ) -> tuple[Any, list[Any]]:

        config = self.tools["semgrep"]

        args = [
            "--config",
            "auto",
            "--json",
            repository_path,
        ]

        result = self.runtime.execute(
            config=config,
            args=args,
            cwd=repository_path,
        )

        findings = self.parse_output(
            "semgrep",
            result.stdout,
        )

        return result, findings

    def run_all_available(
        self,
        repository_path: str,
    ) -> SecurityPipelineResult:

        all_findings = []
        tool_results = {}

        runners = {
            "gitleaks": self.run_gitleaks,
            "trivy": self.run_trivy,
            "semgrep": self.run_semgrep,
        }

        for tool_name, runner in runners.items():

            try:
                result, findings = runner(repository_path)

                tool_results[tool_name] = result
                all_findings.extend(findings)

            except Exception as exc:
                tool_results[tool_name] = {
                    "error": str(exc)
                }

        risk_profile = self.combine_findings(
            all_findings
        )

        return SecurityPipelineResult(
            findings=all_findings,
            risk_profile=risk_profile,
            tool_results=tool_results,
        )