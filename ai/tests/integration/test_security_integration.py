import tempfile

from pathlib import Path

from ai.security.security_pipeline import (
    analyze_security_pipeline
)


def run_test():

    print("=" * 70)
    print("PHASE 2 — SECURITY INTEGRATION TEST")
    print("=" * 70)

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    try:

        (
            repository / "application.py"
        ).write_text(
            """
SECRET = "12345678901234567890"

value = input("value: ")

result = eval(value)
""",
            encoding="utf-8"
        )

        result = analyze_security_pipeline(
            repository
        )

        assert result["success"] is True

        print(
            "[PASS] Security pipeline"
        )

        assert (
            result[
                "secretAnalysis"
            ][
                "totalFindings"
            ] > 0
        )

        print(
            "[PASS] Secret scanner integration"
        )

        assert (
            result[
                "staticAnalysis"
            ][
                "totalFindings"
            ] > 0
        )

        print(
            "[PASS] Static analyzer integration"
        )

        assert (
            "threatAnalysis"
            in result
        )

        print(
            "[PASS] Threat analyzer integration"
        )

        print("=" * 70)
        print(
            "SECURITY INTEGRATION PASSED"
        )
        print("=" * 70)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_test()