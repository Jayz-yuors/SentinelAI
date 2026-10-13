from pathlib import Path
from .git_command import GitCommandExecutor, GitCommandResult
from .git_repository import GitRepository


class GitService:

    def __init__(self, timeout_seconds: int = 120):
        self.executor = GitCommandExecutor(timeout_seconds)

    def clone(
        self,
        repository_url: str,
        destination: str,
        branch: str | None = None,
    ) -> GitCommandResult:

        if not repository_url:
            raise ValueError("Repository URL is required.")

        destination_path = Path(destination).resolve()

        args = ["clone"]

        if branch:
            args.extend(["--branch", branch])

        args.extend([
            repository_url,
            str(destination_path),
        ])

        return self.executor.run(args)

    def fetch(
        self,
        repository_path: str,
    ) -> GitCommandResult:

        return self.executor.run(
            ["fetch", "--all", "--prune"],
            cwd=repository_path,
        )

    def status(
        self,
        repository_path: str,
    ) -> GitCommandResult:

        return self.executor.run(
            ["status", "--short", "--branch"],
            cwd=repository_path,
        )

    def diff(
        self,
        repository_path: str,
        base: str | None = None,
        head: str | None = None,
    ) -> GitCommandResult:

        args = ["diff"]

        if base and head:
            args.extend([base, head])

        return self.executor.run(
            args,
            cwd=repository_path,
        )

    def log(
        self,
        repository_path: str,
        limit: int = 20,
    ) -> GitCommandResult:

        if limit <= 0:
            raise ValueError("Log limit must be greater than zero.")

        return self.executor.run(
            [
                "log",
                f"-{limit}",
                "--oneline",
                "--decorate",
            ],
            cwd=repository_path,
        )

    def branches(
        self,
        repository_path: str,
    ) -> GitCommandResult:

        return self.executor.run(
            ["branch", "--all"],
            cwd=repository_path,
        )

    def checkout(
        self,
        repository_path: str,
        branch: str,
    ) -> GitCommandResult:

        if not branch:
            raise ValueError("Branch is required.")

        return self.executor.run(
            ["checkout", branch],
            cwd=repository_path,
        )

    def create_branch(
        self,
        repository_path: str,
        branch: str,
    ) -> GitCommandResult:

        if not branch:
            raise ValueError("Branch is required.")

        return self.executor.run(
            ["switch", "-c", branch],
            cwd=repository_path,
        )

    def switch_branch(
        self,
        repository_path: str,
        branch: str,
    ) -> GitCommandResult:

        return self.executor.run(
            ["switch", branch],
            cwd=repository_path,
        )

    def add(
        self,
        repository_path: str,
        paths: list[str],
    ) -> GitCommandResult:

        if not paths:
            raise ValueError("At least one path is required.")

        return self.executor.run(
            ["add", *paths],
            cwd=repository_path,
        )

    def commit(
        self,
        repository_path: str,
        message: str,
    ) -> GitCommandResult:

        if not message:
            raise ValueError("Commit message is required.")

        return self.executor.run(
            ["commit", "-m", message],
            cwd=repository_path,
        )

    def push(
        self,
        repository_path: str,
        remote: str = "origin",
        branch: str | None = None,
    ) -> GitCommandResult:

        args = ["push", remote]

        if branch:
            args.append(branch)

        return self.executor.run(
            args,
            cwd=repository_path,
        )