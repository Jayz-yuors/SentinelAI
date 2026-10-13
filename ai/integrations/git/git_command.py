from dataclasses import dataclass
import base64
import os
import subprocess
from typing import Optional


@dataclass
class GitCommandResult:
    command: list[str]
    return_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.return_code == 0


class GitCommandExecutor:

    def __init__(self, timeout_seconds: int = 120):
        self.timeout_seconds = timeout_seconds
        self.environment: dict[str, str] = {}

    def set_github_token(self, token: str) -> None:
        """Pass GitHub HTTPS credentials to Git without persisting them in the clone."""
        encoded = base64.b64encode(
            f"x-access-token:{token}".encode("utf-8")
        ).decode("ascii")
        self.environment.update(
            {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {encoded}",
                "GIT_TERMINAL_PROMPT": "0",
            }
        )

    def set_git_identity(self, name: str, email: str) -> None:
        """Apply commit author/committer identity to this executor only."""
        self.environment.update(
            {
                "GIT_AUTHOR_NAME": name,
                "GIT_AUTHOR_EMAIL": email,
                "GIT_COMMITTER_NAME": name,
                "GIT_COMMITTER_EMAIL": email,
            }
        )

    def run(
        self,
        args: list[str],
        cwd: Optional[str] = None,
    ) -> GitCommandResult:

        if not args:
            raise ValueError("Git command arguments cannot be empty.")

        command = ["git", *args]

        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=False,
                env={**os.environ, **self.environment},
            )

            return GitCommandResult(
                command=command,
                return_code=completed.returncode,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
            )

        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(
                f"Git command timed out after "
                f"{self.timeout_seconds} seconds: {' '.join(command)}"
            ) from exc

        except OSError as exc:
            raise RuntimeError(
                f"Unable to execute Git: {exc}"
            ) from exc
