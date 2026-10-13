import tempfile

from pathlib import Path

from ai.security.secrets.secret_scanner import (
    analyze_secrets
)


def run_test():

    print("=" * 70)
    print("PHASE 3 — SECRET SCANNER TEST")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as temp:

        repository = Path(temp)

        test_file = (
            repository
            / "config.py"
        )

        test_file.write_text(
            """
API_KEY = "ABCDEF12345678901234"
PASSWORD = "supersecret123"
TOKEN = "abcdefghijklmnopqrstuvwxyz123456"
""",
            encoding="utf-8"
        )

        result = analyze_secrets(
            repository
        )

        assert result[
            "totalFindings"
        ] >= 3

        categories = {
            item["category"]
            for item in result[
                "findings"
            ]
        }

        assert "API_KEY" in categories
        assert "PASSWORD" in categories
        assert "TOKEN" in categories

        print(
            "[PASS] Secret detection"
        )

        print(
            "[PASS] API key detection"
        )

        print(
            "[PASS] Password detection"
        )

        print(
            "[PASS] Token detection"
        )

    print("=" * 70)
    print("SECRET SCANNER TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()