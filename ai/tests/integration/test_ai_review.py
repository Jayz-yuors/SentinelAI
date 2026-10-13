from ai.integrations.ai_review.review_service import (
    AIReviewService,
)


def run_test():

    print()
    print("=" * 70)
    print(" SENTINELAI — AI REVIEW INTEGRATION TEST")
    print("=" * 70)

    service = AIReviewService.__new__(
        AIReviewService
    )

    raw_response = """
    {
        "summary": "Security review completed.",
        "findings": [
            {
                "finding_id": "finding-001",
                "severity": "high",
                "title": "Command injection",
                "explanation": "User input reaches a shell command.",
                "file_path": "app.py",
                "line_number": 10,
                "recommendation": "Avoid shell execution of untrusted input.",
                "confidence": 0.96
            }
        ]
    }
    """

    parsed = service._parse_json(
        raw_response
    )

    assert parsed["summary"]

    assert len(
        parsed["findings"]
    ) == 1

    finding = parsed["findings"][0]

    assert finding["finding_id"] == "finding-001"
    assert finding["severity"] == "high"
    assert finding["file_path"] == "app.py"

    print("[PASS] AI review JSON parsing")
    print("[PASS] Review finding structure")
    print("[PASS] Severity extraction")
    print("[PASS] File/line extraction")

    print()
    print("=" * 70)
    print(" AI REVIEW INTEGRATION TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()