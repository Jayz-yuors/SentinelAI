import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class GitHubConfig:
    username: str
    token: str
    api_url: str
    base_branch: str

    @classmethod
    def from_environment(
        cls,
        token_override: str | None = None,
    ) -> "GitHubConfig":
        username = os.getenv("GITHUB_USERNAME", "").strip()
        token = (
            token_override
            or os.getenv("GITHUB_TOKEN", "")
        ).strip()

        api_url = os.getenv(
            "GITHUB_API_URL",
            "https://api.github.com",
        ).rstrip("/")

        base_branch = os.getenv(
            "GITHUB_BASE_BRANCH",
            "main",
        ).strip() or "main"

        if not token:
            raise RuntimeError(
                "GITHUB_TOKEN is not configured."
            )

        return cls(
            username=username,
            token=token,
            api_url=api_url,
            base_branch=base_branch,
        )
