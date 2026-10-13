from pathlib import Path
import tempfile

from ai.security.external.tool_service import (
    run_external_security_tools
)


def main():

    repository_path = Path(
        tempfile.mkdtemp(
            prefix="sentinelai_4e_"
        )
    )

    (repository_path / "README.md").write_text(
        "# SentinelAI Phase 4E Test\n",
        encoding="utf-8"
    )

    (repository_path / "test.py").write_text(
        """
import subprocess

def test_function():
    subprocess.call("echo test", shell=True)
""",
        encoding="utf-8"
    )

    result = run_external_security_tools(
        repository_path
    )

    print("")
    print(
        "SENTINELAI — PHASE 4E "
        "EXTERNAL TOOL TEST"
    )
    print("")

    for name, tool in result[
        "tools"
    ].items():

        status = (
            "PASS"
            if tool.get("success")
            else "FAIL"
        )

        print(
            f"[{status}] {name}"
        )

    print("")

    if not result["success"]:

        print(
            "PHASE 4E EXTERNAL TOOL "
            "TEST FAILED"
        )

        raise SystemExit(1)

    print(
        "PHASE 4E EXTERNAL TOOL "
        "TEST PASSED"
    )


if __name__ == "__main__":
    main()