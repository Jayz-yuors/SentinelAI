import re
from dataclasses import dataclass
from urllib.parse import urlparse

from .github_client import GitHubClient
from .github_models import GitHubPullRequest


@dataclass
class GitHubTarget:
    owner: str
    repository: str
    branch: str


class GitHubWorkflow:

    GITHUB_HOSTS = {
        "github.com",
        "www.github.com",
    }

    def __init__(
        self,
        client: GitHubClient | None = None,
    ):
        self.client = client or GitHubClient()

    def parse_repository_url(
        self,
        repository_url: str,
        branch: str | None = None,
    ) -> GitHubTarget:

        parsed = urlparse(
            repository_url.strip()
        )

        if parsed.netloc.lower() not in self.GITHUB_HOSTS:
            raise ValueError(
                "Repository URL is not a GitHub repository."
            )

        parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if len(parts) < 2:
            raise ValueError(
                "Invalid GitHub repository URL."
            )

        owner = parts[0]

        repository = re.sub(
            r"\.git$",
            "",
            parts[1],
        )

        if not owner or not repository:
            raise ValueError(
                "Unable to determine GitHub owner/repository."
            )

        repository_info = self.client.get_repository(
            owner,
            repository,
        )

        selected_branch = (
            branch
            or repository_info.default_branch
            or "main"
        )

        return GitHubTarget(
            owner=owner,
            repository=repository,
            branch=selected_branch,
        )

    def verify_access(
        self,
        target: GitHubTarget,
    ) -> dict:

        user = self.client.get_authenticated_user()

        repository = self.client.get_repository(
            target.owner,
            target.repository,
        )

        result = {
            "authenticated_user": user.get(
                "login"
            ),
            "repository": repository.full_name,
            "branch": target.branch,
            "branch_exists": False,
            "branch_sha": None,
            "repository_empty": False,
        }

        try:
            branch = self.client.get_branch(
                target.owner,
                target.repository,
                target.branch,
            )

            result["branch_exists"] = True
            result["branch_sha"] = branch.sha

        except RuntimeError as exc:

            message = str(exc)

            if "HTTP 404" in message:
                result["repository_empty"] = True
            else:
                raise

        return result

    def authenticated_user(self) -> dict:
        return self.client.get_authenticated_user()

    def create_remote_branch(
        self,
        target: GitHubTarget,
        candidate_branch: str,
    ) -> dict:

        branch = self.client.get_branch(
            target.owner,
            target.repository,
            target.branch,
        )

        return self.client.create_branch(
            target.owner,
            target.repository,
            candidate_branch,
            branch.sha,
        )

    def create_pull_request(
        self,
        target: GitHubTarget,
        candidate_branch: str,
        title: str,
        body: str,
    ) -> GitHubPullRequest:

        return self.client.create_pull_request(
            owner=target.owner,
            repository=target.repository,
            title=title,
            body=body,
            head=candidate_branch,
            base=target.branch,
        )
