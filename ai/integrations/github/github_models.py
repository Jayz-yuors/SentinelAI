from dataclasses import dataclass
from typing import Any


@dataclass
class GitHubRepository:
    owner: str
    name: str
    default_branch: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


@dataclass
class GitHubBranch:
    name: str
    sha: str


@dataclass
class GitHubPullRequest:
    number: int
    title: str
    url: str
    state: str
    head_branch: str
    base_branch: str


@dataclass
class GitHubApiResult:
    status_code: int
    data: Any

    @property
    def success(self) -> bool:
        return 200 <= self.status_code < 300