from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def ask(label: str, default: str | None = None) -> str:
    """
    Ask the user for a value.

    If a default is provided, pressing Enter accepts it.
    """
    if default is not None:
        value = input(f"{label} [{default}]: ").strip()
        return value if value else default

    value = input(label).strip()

    if not value:
        print("ERROR: value is required.")
        raise SystemExit(1)

    return value


def ask_yes_no(label: str, default: bool = False) -> bool:
    """
    Ask for a YES/NO confirmation.
    """
    default_text = "YES" if default else "NO"

    value = input(f"{label} [{default_text}]: ").strip().upper()

    if not value:
        return default

    return value in {"YES", "Y"}


def main() -> int:
    print("=" * 70)
    print("SENTINELAI — GENERIC LOCAL REMEDIATION")
    print("=" * 70)

    # ------------------------------------------------------------------
    # LOCAL FILE
    # ------------------------------------------------------------------

    local_file = Path(
        ask("Enter FULL path of your local replacement file: ")
    ).expanduser().resolve()

    if not local_file.is_file():
        print(f"[FAIL] Local replacement not found:")
        print(f"       {local_file}")
        return 1

    # ------------------------------------------------------------------
    # GITHUB REPOSITORY
    # ------------------------------------------------------------------

    repository_url = ask(
        "Enter GitHub repository URL: "
    )

    # ------------------------------------------------------------------
    # TARGET FILE
    # ------------------------------------------------------------------

    target_input = ask(
        "Enter target file path inside the repository: "
    )

    target = Path(target_input)

    if target.is_absolute():
        print(
            "[FAIL] Target must be a repository-relative path, "
            "not an absolute path."
        )
        return 1

    # Normalize Windows separators for CLI consistency.
    target = Path(str(target).replace("\\", "/"))

    # ------------------------------------------------------------------
    # BASE BRANCH
    # ------------------------------------------------------------------

    base_branch = ask(
        "Enter base branch",
        "main",
    )

    # ------------------------------------------------------------------
    # DEVELOPER REASON
    # ------------------------------------------------------------------

    reason = ask(
        "Reason for proposed update: "
    )

    if len(reason) < 20:
        print("[FAIL] Reason must contain at least 20 characters.")
        return 1

    # ------------------------------------------------------------------
    # PUSH
    # ------------------------------------------------------------------

    print("\n" + "=" * 70)
    print("GITHUB PUSH CONFIGURATION")
    print("=" * 70)

    print(
        "\nPUSH is ENABLED for this workflow."
    )

    print(
        "SentinelAI will create a candidate branch and push it to GitHub."
    )

    print(
        "The base branch will NOT be modified directly."
    )

    push_enabled = ask_yes_no(
        "\nEnable GitHub push? (YES/NO)",
        default=True,
    )

    if not push_enabled:
        print(
            "\n[INFO] Push disabled by user."
        )
        print(
            "[INFO] This run will stop after local candidate validation."
        )

    # ------------------------------------------------------------------
    # DISPLAY REQUEST
    # ------------------------------------------------------------------

    print("\n" + "=" * 70)
    print("SENTINELAI ANALYSIS REQUEST")
    print("=" * 70)

    print(f"Local replacement : {local_file}")
    print(f"GitHub repository : {repository_url}")
    print(f"Base branch       : {base_branch}")
    print(f"Target            : {target}")
    print(f"Developer reason  : {reason}")
    print(f"Push enabled      : {push_enabled}")

    print("\nWorkflow:")
    print("  ORIGINAL -> LOCAL")
    print("  -> AI REVIEW")
    print("  -> AI REMEDIATION")
    print("  -> VERIFICATION")
    print("  -> CANDIDATE BRANCH")
    print("  -> COMMIT")
    
    if push_enabled:
        print("  -> PUSH")
        print("  -> GITHUB PR")

    print("\nSafety:")
    print("  Base branch is never edited directly.")
    print("  SentinelAI operates on a candidate branch.")
    print("  Failed verification must not be pushed.")
    print("  GitHub credentials are handled by the configured GitHub client.")

    # ------------------------------------------------------------------
    # FINAL CONFIRMATION
    # ------------------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL CONFIRMATION")
    print("=" * 70)

    confirmation = ask(
        "\nStart SentinelAI workflow? (YES/NO): "
    ).upper()

    if confirmation != "YES":
        print("Workflow cancelled.")
        return 0

    # ------------------------------------------------------------------
    # BUILD CLI COMMAND
    # ------------------------------------------------------------------

    project_root = Path(__file__).resolve().parent.parent

    command = [
        sys.executable,
        "-m",
        "ai.cli.main",
        "remediate-local",
        "--repository-url",
        repository_url,
        "--target",
        str(target),
        "--local-file",
        str(local_file),
        "--reason",
        reason,
        "--base-branch",
        base_branch,
    ]

    # ------------------------------------------------------------------
    # ENABLE PUSH
    # ------------------------------------------------------------------

    if push_enabled:
        command.append("--push")

    # ------------------------------------------------------------------
    # EXECUTE
    # ------------------------------------------------------------------

    print("\n" + "=" * 70)
    print("SENTINELAI — STARTING WORKFLOW")
    print("=" * 70)

    print("\nCommand:")
    print(" ".join(f'"{arg}"' if " " in arg else arg for arg in command))

    print()

    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            check=False,
        )

    except KeyboardInterrupt:
        print("\n[FAIL] Workflow interrupted by user.")
        return 130

    except Exception as exc:
        print("\n[FAIL] Unable to start SentinelAI workflow.")
        print(f"       {exc}")
        return 1

    # ------------------------------------------------------------------
    # RESULT
    # ------------------------------------------------------------------

    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("SENTINELAI WORKFLOW COMPLETED")
        print("=" * 70)

        if push_enabled:
            print("[PASS] Local remediation workflow completed.")
            print("[PASS] Push was enabled.")
            print("[INFO] Check the workflow result above for candidate branch,")
            print("       commit SHA and Pull Request URL.")
        else:
            print("[PASS] Local remediation validation completed.")
            print("[INFO] Push was disabled for this run.")

    else:
        print("\n" + "=" * 70)
        print("SENTINELAI WORKFLOW FAILED")
        print("=" * 70)

        print(
            f"[FAIL] SentinelAI exited with code {result.returncode}."
        )

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())