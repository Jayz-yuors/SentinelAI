import os

from dotenv import load_dotenv

from .tool_config import SecurityToolConfig

load_dotenv()


def get_security_tools() -> dict[str, SecurityToolConfig]:

    return {
        "gitleaks": SecurityToolConfig(
            name="gitleaks",
            executable=os.getenv(
                "SENTINELAI_GITLEAKS_PATH",
                r"C:\Tools\gitleaks\gitleaks.exe",
            ),
        ),

        "trivy": SecurityToolConfig(
            name="trivy",
            executable=os.getenv(
                "SENTINELAI_TRIVY_PATH",
                r"C:\Tools\trivy-0.74.0\trivy.exe",
            ),
        ),

        "semgrep": SecurityToolConfig(
            name="semgrep",
            executable=os.getenv(
                "SENTINELAI_SEMGREP_PATH",
                "semgrep",
            ),
        ),

        "dependency-check": SecurityToolConfig(
            name="dependency-check",
            executable=os.getenv(
                "SENTINELAI_DEPENDENCY_CHECK_PATH",
                r"C:\Tools\dependency-check\bin\dependency-check.bat",
            ),
        ),

        "sonar": SecurityToolConfig(
            name="sonar",
            executable=os.getenv(
                "SENTINELAI_SONAR_SCANNER_PATH",
                r"C:\Tools\sonar-scanner-8.1.0.6389-windows-x64\bin\sonar-scanner.bat",
            ),
        ),
    }