from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from .git_command import GitCommandExecutor


@dataclass
class CandidateBranch:
    original_branch: str
    candidate_branch: str
    repository_path: str


class CandidateBranchManager:

    def __init__(
        self,
        executor: GitCommandExecutor | None = None,
    ):
        self.executor = (
            executor
            or GitCommandExecutor()
        )

    def configure_identity(
        self,
        repository_path: str,
        name: str,
        email: str,
    ) -> None:
        if not name.strip() or not email.strip():
            raise ValueError(
                "Git commit identity requires a name and email."
            )

        for key, value in (
            ("user.name", name.strip()),
            ("user.email", email.strip()),
        ):
            result = self.executor.run(
                ["config", key, value],
                cwd=repository_path,
            )
            if not result.success:
                raise RuntimeError(
                    f"Unable to configure Git {key}: {result.stderr}"
                )

    def current_branch(
        self,
        repository_path: str,
    ) -> str:

        result = self.executor.run(
            ["branch", "--show-current"],
            cwd=repository_path,
        )

        if not result.success:
            raise RuntimeError(
                f"Unable to determine current branch: "
                f"{result.stderr}"
            )

        branch = result.stdout.strip()

        if not branch:
            raise RuntimeError(
                "Repository is not currently on a named branch."
            )

        return branch

    def create_candidate(
        self,
        repository_path: str,
        prefix: str = "sentinelai",
    ) -> CandidateBranch:

        original = self.current_branch(
            repository_path
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        )

        candidate = (
            f"{prefix}/"
            f"security-remediation-{timestamp}"
        )

        result = self.executor.run(
            ["switch", "-c", candidate],
            cwd=repository_path,
        )

        if not result.success:
            raise RuntimeError(
                f"Unable to create candidate branch: "
                f"{result.stderr}"
            )

        return CandidateBranch(
            original_branch=original,
            candidate_branch=candidate,
            repository_path=str(
                Path(repository_path).resolve()
            ),
        )

    def has_changes(
        self,
        repository_path: str,
    ) -> bool:

        result = self.executor.run(
            ["status", "--porcelain"],
            cwd=repository_path,
        )

        if not result.success:
            raise RuntimeError(
                f"Unable to inspect repository status: "
                f"{result.stderr}"
            )

        return bool(result.stdout.strip())

    def commit_changes(
        self,
        repository_path: str,
        message: str,
    ) -> str:

        add_result = self.executor.run(
            ["add", "."],
            cwd=repository_path,
        )

        if not add_result.success:
            raise RuntimeError(
                f"Git add failed: {add_result.stderr}"
            )

        commit_result = self.executor.run(
            [
                "commit",
                "-m",
                message,
            ],
            cwd=repository_path,
        )

        if not commit_result.success:
            raise RuntimeError(
                f"Git commit failed: {commit_result.stderr}"
            )

        log_result = self.executor.run(
            [
                "log",
                "-1",
                "--pretty=%H",
            ],
            cwd=repository_path,
        )

        if not log_result.success:
            raise RuntimeError(
                f"Unable to retrieve commit SHA: "
                f"{log_result.stderr}"
            )

        return log_result.stdout.strip()

    def push(
        self,
        repository_path: str,
        branch: str,
        remote: str = "origin",
    ) -> None:

        result = self.executor.run(
            [
                "push",
                "-u",
                remote,
                branch,
            ],
            cwd=repository_path,
        )

        if not result.success:
            raise RuntimeError(
                f"Git push failed: {result.stderr}"
            )

    def checkout(
        self,
        repository_path: str,
        branch: str,
    ) -> None:

        result = self.executor.run(
            ["switch", branch],
            cwd=repository_path,
        )

        if not result.success:
            raise RuntimeError(
                f"Unable to switch to {branch}: "
                f"{result.stderr}"
            )
