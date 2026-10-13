import tempfile

from pathlib import Path

from ai.security.static_analysis.security_analyzer import (
    analyze_security
)


def run_test():

    print("=" * 70)
    print("PHASE 3 — STATIC SECURITY ANALYZER TEST")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as temp:

        repository = Path(temp)

        source_file = (
            repository
            / "unsafe.py"
        )

        source_file.write_text(
            """
user_input = input("Enter value")
result = eval(user_input)
""",
            encoding="utf-8"
        )

        result = analyze_security(
            repository
        )

        assert result[
            "totalFindings"
        ] >= 2

        categories = {
            item["category"]
            for item in result[
                "findings"
            ]
        }

        assert (
            "DANGEROUS_FUNCTION"
            in categories
        )

        print(
            "[PASS] Static analysis"
        )

        print(
            "[PASS] Dangerous function detection"
        )

    print("=" * 70)
    print("STATIC SECURITY ANALYZER TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()