from ai.security.runtime.command_runner import CommandRunner


def main():

    print()
    print("=" * 60)
    print(" SENTINELAI — PHASE 5 SECURITY RUNTIME TEST")
    print("=" * 60)
    print()

    print("[1] Testing command runner...")

    result = CommandRunner.run(
        ["git", "--version"],
        timeout=10
    )

    assert result["returncode"] == 0
    assert "git version" in result["stdout"].lower()

    print("[PASS] Command runner")

    print()
    print("[2] Execution metadata...")

    assert result["execution_time_ms"] >= 0
    assert result["timed_out"] is False

    print("[PASS] Execution metadata")

    print()
    print("=" * 60)
    print(" PHASE 5 SECURITY RUNTIME TEST PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()