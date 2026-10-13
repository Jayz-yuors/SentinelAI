import subprocess

from .tool_config import SecurityToolConfig
from .tool_result import SecurityToolResult


class SecurityToolRuntime:

    def __init__(
        self,
        timeout_seconds: int = 300,
    ):
        self.timeout_seconds = (
            timeout_seconds
        )

    def execute(
        self,
        config: SecurityToolConfig,
        args: list[str],
        cwd: str | None = None,
    ) -> SecurityToolResult:

        if not config.enabled:
            raise RuntimeError(
                f"Security tool is disabled: "
                f"{config.name}"
            )

        command = [
            config.executable,
            *args,
        ]

        try:

            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=(
                    config.timeout_seconds
                    or self.timeout_seconds
                ),
                shell=False,
            )

            return SecurityToolResult(
                tool=config.name,
                command=command,
                return_code=(
                    completed.returncode
                ),
                stdout=completed.stdout,
                stderr=completed.stderr,
            )

        except subprocess.TimeoutExpired as exc:

            raise TimeoutError(
                f"{config.name} timed out "
                f"after "
                f"{config.timeout_seconds} "
                f"seconds."
            ) from exc

        except OSError as exc:

            raise RuntimeError(
                f"Unable to execute "
                f"{config.name}: {exc}"
            ) from exc