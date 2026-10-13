import tempfile

from pathlib import Path

from ai.dependency.dependency_pipeline import (
    analyze_dependencies
)


def run_test():

    print("=" * 70)
    print("PHASE 2 — DEPENDENCY INTEGRATION TEST")
    print("=" * 70)

    temporary_directory = (
        tempfile.TemporaryDirectory()
    )

    repository = Path(
        temporary_directory.name
    )

    try:

        (
            repository / "main.py"
        ).write_text(
            """
import helper
from utils import test
""",
            encoding="utf-8"
        )

        (
            repository / "helper.py"
        ).write_text(
            """
def hello():
    return True
""",
            encoding="utf-8"
        )

        (
            repository / "utils.py"
        ).write_text(
            """
def test():
    return True
""",
            encoding="utf-8"
        )

        result = analyze_dependencies(
            repository
        )

        assert result["success"] is True

        print(
            "[PASS] Dependency pipeline"
        )

        assert (
            len(
                result[
                    "dependencyExtraction"
                ]
            ) == 3
        )

        print(
            "[PASS] Dependency extraction"
        )

        assert (
            len(
                result[
                    "dependencyGraph"
                ][
                    "nodes"
                ]
            ) > 0
        )

        print(
            "[PASS] Graph generation"
        )

        assert (
            len(
                result[
                    "dependencyGraph"
                ][
                    "edges"
                ]
            ) > 0
        )

        print(
            "[PASS] Graph relationships"
        )

        assert (
            "dependencyRisk"
            in result
        )

        print(
            "[PASS] Dependency risk"
        )

        print("=" * 70)
        print(
            "DEPENDENCY INTEGRATION PASSED"
        )
        print("=" * 70)

    finally:

        temporary_directory.cleanup()


if __name__ == "__main__":
    run_test()