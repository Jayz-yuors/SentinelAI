import tempfile
from pathlib import Path

from ai.integrations.git import GitService


def run_test():
    print()
    print("=" * 70)
    print(" SENTINELAI — GIT RUNTIME INTEGRATION TEST")
    print("=" * 70)

    git = GitService()

    with tempfile.TemporaryDirectory() as temp_dir:

        repo_path = Path(temp_dir) / "test-repository"
        repo_path.mkdir(parents=True, exist_ok=True)

        print("\n[1] Creating temporary Git repository...")

        result = git.executor.run(
            ["init", "-b", "main"],
            cwd=str(repo_path),
        )

        assert result.success, result.stderr

        print("[PASS] Git repository initialized")

        print("\n[2] Creating test file...")

        test_file = repo_path / "test.txt"

        test_file.write_text(
            "SentinelAI Git Runtime Test\n",
            encoding="utf-8",
        )

        print("[PASS] Test file created")

        print("\n[3] Testing status...")

        result = git.status(str(repo_path))

        assert result.success
        assert "test.txt" in result.stdout

        print("[PASS] Git status")

        print("\n[4] Testing add...")

        result = git.add(
            str(repo_path),
            ["test.txt"],
        )

        assert result.success, result.stderr

        print("[PASS] Git add")

        print("\n[5] Testing commit...")

        result = git.commit(
            str(repo_path),
            "test: SentinelAI Git runtime",
        )

        assert result.success, result.stderr

        print("[PASS] Git commit")

        print("\n[6] Testing log...")

        result = git.log(
            str(repo_path),
            limit=5,
        )

        assert result.success
        assert "SentinelAI Git runtime" in result.stdout

        print("[PASS] Git log")

        print("\n[7] Testing branch creation...")

        result = git.create_branch(
            str(repo_path),
            "sentinelai/test-branch",
        )

        assert result.success, result.stderr

        print("[PASS] Branch creation")

        print("\n[8] Testing branch listing...")

        result = git.branches(str(repo_path))

        assert result.success
        assert "sentinelai/test-branch" in result.stdout

        print("[PASS] Branch listing")

        print("\n[9] Testing branch switch...")

        result = git.switch_branch(
            str(repo_path),
            "main",
        )

        assert result.success, result.stderr

        print("[PASS] Branch switch")

        print("\n[10] Testing diff...")

        test_file.write_text(
            "SentinelAI Git Runtime Test\nModified\n",
            encoding="utf-8",
        )

        result = git.diff(str(repo_path))

        assert result.success
        assert "Modified" in result.stdout

        print("[PASS] Git diff")

    print()
    print("=" * 70)
    print(" GIT RUNTIME INTEGRATION TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()