from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitRepository:
    path: Path

    def __post_init__(self):
        self.path = self.path.resolve()

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def git_directory(self) -> Path:
        return self.path / ".git"

    @property
    def is_git_repository(self) -> bool:
        return self.git_directory.exists()