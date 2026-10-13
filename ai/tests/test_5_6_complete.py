from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ai.integrations.git.git_command import (
    GitCommandExecutor,
)

from ai.integrations.git.candidate_manager import (
    CandidateBranchManager,
)

from ai.integrations.security.security_gate import (
    SecurityGate,
)

from ai.integrations.github.github_config import (
    GitHubConfig,
)

from ai.integrations.github.github_client import (
    GitHubClient,
)

from ai.integrations.github.github_workflow import (
    GitHubWorkflow,
)

from ai.integrations.ai_review.comparison_service import (
    ComparisonService,
)


def assert_true(
    condition,
    message,
):

    if not condition:
        raise AssertionError(
            message
        )

    print(
        f"[PASS] {message}"
    )


def test_git_runtime():

    executor = GitCommandExecutor()

    result = executor.run(
        ["--version"]
    )

    assert_true(
        result.success,
        "Git executable",
    )


def test_candidate_branch():

    with tempfile.TemporaryDirectory() as temp:

        path = Path(temp)

        executor = GitCommandExecutor()

        executor.run(
            ["init", "-b", "main"],
            cwd=str(path),
        )

        (path / "README.md").write_text(
            "SentinelAI test repository\n",
            encoding="utf-8",
        )

        executor.run(
            ["add", "."],
            cwd=str(path),
        )

        commit = executor.run(
            [
                "-c",
                "user.name=SentinelAI Test",
                "-c",
                "user.email=sentinelai@test.local",
                "commit",
                "-m",
                "initial",
            ],
            cwd=str(path),
        )

        assert_true(
            commit.success,
            "Temporary Git repository",
        )

        manager = CandidateBranchManager(
            executor
        )

        candidate = manager.create_candidate(
            str(path)
        )

        assert_true(
            candidate.original_branch == "main",
            "Candidate original branch",
        )

        assert_true(
            candidate.candidate_branch.startswith(
                "sentinelai/"
            ),
            "Candidate branch created",
        )

        current = manager.current_branch(
            str(path)
        )

        assert_true(
            current == candidate.candidate_branch,
            "Candidate branch active",
        )


def test_security_gate():

    class FakeProfile:

        overall_score = 20
        overall_level = "LOW"

        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 1,
            "low": 0,
            "info": 0,
        }

    gate = SecurityGate(
        max_score=50,
        block_critical=True,
        block_high=False,
    )

    result = gate.evaluate(
        FakeProfile()
    )

    assert_true(
        result.allowed,
        "Security gate allows safe result",
    )

    class BlockedProfile:

        overall_score = 80
        overall_level = "CRITICAL"

        severity_counts = {
            "critical": 1,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

    result = gate.evaluate(
        BlockedProfile()
    )

    assert_true(
        not result.allowed,
        "Security gate blocks unsafe result",
    )


def test_comparison():

    service = ComparisonService()

    before = {
        "overall_score": 80,
        "overall_level": "CRITICAL",
    }

    after = {
        "overall_score": 25,
        "overall_level": "MEDIUM",
    }

    result = service.compare(
        before,
        after,
    )

    assert_true(
        result.improved,
        "Risk comparison detects improvement",
    )

    assert_true(
        result.score_delta == -55,
        "Risk delta calculated",
    )


def test_github_configuration():

    config = GitHubConfig.from_environment()

    assert_true(
        bool(config.token),
        "GitHub token configured",
    )

    assert_true(
        config.api_url.startswith(
            "https://"
        ),
        "GitHub API configured",
    )


def test_github_auth():

    client = GitHubClient()

    user = client.get_authenticated_user()

    assert_true(
        user.get("login")
        == "Jayz-yuors",
        "GitHub authentication",
    )


def test_github_repository():

    workflow = GitHubWorkflow()

    target = workflow.parse_repository_url(
        "https://github.com/Jayz-yuors/SentinelAI"
    )

    assert_true(
        target.owner == "Jayz-yuors",
        "GitHub owner discovery",
    )

    assert_true(
        target.repository == "SentinelAI",
        "GitHub repository discovery",
    )


def main():

    print()
    print("=" * 60)
    print("SENTINELAI — PHASE 5 + 6 ESSENTIAL TEST")
    print("=" * 60)
    print()

    test_git_runtime()

    test_candidate_branch()

    test_security_gate()

    test_comparison()

    test_github_configuration()

    test_github_auth()

    test_github_repository()

    print()
    print("=" * 60)
    print("PHASE 5 + 6 ESSENTIAL TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()