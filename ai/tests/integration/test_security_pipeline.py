import tempfile
from pathlib import Path

from ai.integrations.security.security_pipeline import (
    SecurityPipeline,
)


def create_test_repository(
    path: Path,
):

    (
        path / "requirements.txt"
    ).write_text(
        "requests==2.19.0\n",
        encoding="utf-8",
    )

    (
        path / "app.py"
    ).write_text(
        '''
import subprocess

API_KEY = "sk-test-sentinelai-demo-key"


def run_command(user_input):
    subprocess.call(
        user_input,
        shell=True
    )


print(API_KEY)
''',
        encoding="utf-8",
    )

    (
        path / "README.md"
    ).write_text(
        "# SentinelAI Scanner Integration Test\n",
        encoding="utf-8",
    )


def run_test():

    print()
    print("=" * 70)
    print(
        " SENTINELAI — REAL SECURITY PIPELINE TEST"
    )
    print("=" * 70)

    with tempfile.TemporaryDirectory() as temp_dir:

        repository = Path(
            temp_dir
        )

        print(
            "\n[1] Creating synthetic "
            "test repository..."
        )

        create_test_repository(
            repository
        )

        print(
            "[PASS] Test repository created"
        )

        print(
            "\n[2] Running security pipeline..."
        )

        pipeline = SecurityPipeline()

        result = (
            pipeline.run_all_available(
                str(repository)
            )
        )

        print(
            f"[INFO] Total findings: "
            f"{len(result.findings)}"
        )

        # -------------------------------------------------
        # TOOL EXECUTION VALIDATION
        # -------------------------------------------------

        for tool_name, tool_result in (
            result.tool_results.items()
        ):

            if isinstance(
                tool_result,
                dict,
            ):

                print(
                    f"[WARN] {tool_name}: "
                    f"{tool_result.get('error')}"
                )

                continue

            print(
                f"[INFO] {tool_name}: "
                f"return_code="
                f"{tool_result.return_code}"
            )

            if tool_result.stderr:

                print(
                    f"[INFO] {tool_name} stderr: "
                    f"{tool_result.stderr[:300]}"
                )

        assert result.tool_results, (
            "No security tool results "
            "were returned."
        )

        print(
            "[PASS] Security tools executed"
        )

        # -------------------------------------------------
        # FINDING VALIDATION
        # -------------------------------------------------

        assert len(
            result.findings
        ) > 0, (
            "Security pipeline returned "
            "zero findings. "
            "Scanner execution or parsing "
            "is not working."
        )

        print(
            "[PASS] Real findings detected"
        )

        # -------------------------------------------------
        # NORMALIZATION
        # -------------------------------------------------

        print(
            "\n[3] Validating finding normalization..."
        )

        for finding in result.findings:

            assert finding.source
            assert finding.rule_id
            assert finding.severity
            assert finding.message

        print(
            "[PASS] Findings normalized"
        )

        # -------------------------------------------------
        # RISK ENGINE
        # -------------------------------------------------

        print(
            "\n[4] Validating unified "
            "risk engine..."
        )

        assert (
            result.risk_profile
            is not None
        )

        assert (
            result.risk_profile.finding_count
            > 0
        )

        print(
            "[PASS] Unified Risk Engine "
            "processed findings"
        )

        # -------------------------------------------------
        # RISK PROFILE
        # -------------------------------------------------

        print(
            "\n[5] Risk profile:"
        )

        print(
            result.risk_profile
        )

        print()
        print("=" * 70)
        print(
            " REAL SECURITY PIPELINE "
            "TEST PASSED"
        )
        print("=" * 70)


if __name__ == "__main__":
    run_test()