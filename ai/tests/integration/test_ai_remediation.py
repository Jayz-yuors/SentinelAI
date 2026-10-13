import tempfile
from pathlib import Path

from ai.integrations.ai_review.remediation_service import (
    AIRemediationService,
)

from ai.integrations.ai_review.review_models import (
    CodeReviewFinding,
    RemediationProposal,
)


def run_test():

    print()
    print("=" * 70)
    print(" SENTINELAI — AI REMEDIATION INTEGRATION TEST")
    print("=" * 70)

    finding = CodeReviewFinding(
        finding_id="finding-001",
        severity="high",
        title="Unsafe shell execution",
        explanation=(
            "User-controlled input reaches "
            "shell execution."
        ),
        file_path="app.py",
        line_number=5,
        recommendation=(
            "Avoid shell execution of "
            "untrusted input."
        ),
        confidence=0.95,
    )

    proposal = RemediationProposal(
        finding_id="finding-001",
        file_path="app.py",
        explanation="Replace unsafe execution.",
        original_code=(
            "subprocess.call(user_input, shell=True)"
        ),
        replacement_code=(
            "subprocess.run([user_input], shell=False)"
        ),
        patch="test patch",
        confidence=0.92,
    )

    service = AIRemediationService.__new__(
        AIRemediationService
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        repository = Path(temp_dir)

        file_path = repository / "app.py"

        file_path.write_text(
            """
import subprocess

def run(user_input):
    subprocess.call(user_input, shell=True)
""",
            encoding="utf-8",
        )

        print("\n[1] Applying remediation...")

        result = service.apply_proposal(
            str(repository),
            proposal,
        )

        assert result.exists()

        updated = result.read_text(
            encoding="utf-8"
        )

        assert (
            "shell=True"
            not in updated
        )

        assert (
            "shell=False"
            in updated
        )

        print("[PASS] Remediation applied")

        print("\n[2] Validating repository boundary...")

        try:

            bad_proposal = RemediationProposal(
                finding_id="bad",
                file_path="../outside.py",
                explanation="bad",
                original_code="x",
                replacement_code="y",
                patch="",
            )

            service.apply_proposal(
                str(repository),
                bad_proposal,
            )

            raise AssertionError(
                "Path traversal was not blocked"
            )

        except ValueError:

            print(
                "[PASS] Path traversal blocked"
            )

    print()
    print("=" * 70)
    print(" AI REMEDIATION INTEGRATION TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()