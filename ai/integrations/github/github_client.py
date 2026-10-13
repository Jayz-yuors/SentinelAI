import json
import urllib.error
import urllib.request
from typing import Any

from .github_config import GitHubConfig
from .github_models import (
    GitHubApiResult,
    GitHubBranch,
    GitHubPullRequest,
    GitHubRepository,
)


class GitHubClient:

    def __init__(self, config: GitHubConfig | None = None):
        self.config = config or GitHubConfig.from_environment()

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> GitHubApiResult:

        url = f"{self.config.api_url}/{path.lstrip('/')}"

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.config.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "SentinelAI",
        }

        data = None

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url=url,
            data=data,
            headers=headers,
            method=method.upper(),
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=30,
            ) as response:

                body = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

                parsed = (
                    json.loads(body)
                    if body
                    else {}
                )

                return GitHubApiResult(
                    status_code=response.status,
                    data=parsed,
                )

        except urllib.error.HTTPError as exc:

            body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {
                    "message": body
                }

            return GitHubApiResult(
                status_code=exc.code,
                data=parsed,
            )

        except urllib.error.URLError as exc:

            raise RuntimeError(
                f"GitHub API connection failed: {exc}"
            ) from exc

    # ---------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------

    def get_authenticated_user(self) -> dict[str, Any]:

        result = self._request(
            "GET",
            "/user",
        )

        self._ensure_success(
            result,
            "GitHub authentication check failed",
        )

        return result.data

    # ---------------------------------------------------------
    # Repository
    # ---------------------------------------------------------

    def get_repository(
        self,
        owner: str,
        repository: str,
    ) -> GitHubRepository:

        result = self._request(
            "GET",
            f"/repos/{owner}/{repository}",
        )

        self._ensure_success(
            result,
            "Unable to retrieve GitHub repository",
        )

        data = result.data

        return GitHubRepository(
            owner=data["owner"]["login"],
            name=data["name"],
            default_branch=data.get(
                "default_branch",
                self.config.base_branch,
            ),
        )

    # ---------------------------------------------------------
    # Branch
    # ---------------------------------------------------------

    def get_branch(
        self,
        owner: str,
        repository: str,
        branch: str,
    ) -> GitHubBranch:

        result = self._request(
            "GET",
            f"/repos/{owner}/{repository}/branches/{branch}",
        )

        self._ensure_success(
            result,
            f"Unable to retrieve branch '{branch}'",
        )

        return GitHubBranch(
            name=result.data["name"],
            sha=result.data["commit"]["sha"],
        )

    # ---------------------------------------------------------
    # Create branch
    # ---------------------------------------------------------

    def create_branch(
        self,
        owner: str,
        repository: str,
        branch: str,
        sha: str,
    ) -> dict[str, Any]:

        result = self._request(
            "POST",
            f"/repos/{owner}/{repository}/git/refs",
            {
                "ref": f"refs/heads/{branch}",
                "sha": sha,
            },
        )

        self._ensure_success(
            result,
            f"Unable to create branch '{branch}'",
        )

        return result.data

    # ---------------------------------------------------------
    # Pull Request
    # ---------------------------------------------------------

    def create_pull_request(
        self,
        owner: str,
        repository: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> GitHubPullRequest:

        result = self._request(
            "POST",
            f"/repos/{owner}/{repository}/pulls",
            {
                "title": title,
                "body": body,
                "head": head,
                "base": base,
            },
        )

        self._ensure_success(
            result,
            "Unable to create GitHub Pull Request",
        )

        data = result.data

        return GitHubPullRequest(
            number=data["number"],
            title=data["title"],
            url=data["html_url"],
            state=data["state"],
            head_branch=data["head"]["ref"],
            base_branch=data["base"]["ref"],
        )

    # ---------------------------------------------------------
    # Pull Request status
    # ---------------------------------------------------------

    def get_pull_request(
        self,
        owner: str,
        repository: str,
        number: int,
    ) -> GitHubPullRequest:

        result = self._request(
            "GET",
            f"/repos/{owner}/{repository}/pulls/{number}",
        )

        self._ensure_success(
            result,
            "Unable to retrieve Pull Request",
        )

        data = result.data

        return GitHubPullRequest(
            number=data["number"],
            title=data["title"],
            url=data["html_url"],
            state=data["state"],
            head_branch=data["head"]["ref"],
            base_branch=data["base"]["ref"],
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _ensure_success(
        result: GitHubApiResult,
        message: str,
    ) -> None:

        if result.success:
            return

        details = result.data

        if isinstance(details, dict):
            details = details.get(
                "message",
                details,
            )

        raise RuntimeError(
            f"{message}: HTTP {result.status_code} - {details}"
        )