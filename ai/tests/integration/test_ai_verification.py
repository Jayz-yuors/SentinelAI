from dataclasses import dataclass

from ai.integrations.ai_review.comparison_service import (
    RiskComparisonService,
)


@dataclass
class FakeFinding:
    fingerprint: str


@dataclass
class FakeProfile:
    overall_score: float
    overall_level: str
    findings: list


def run_test():

    print()
    print("=" * 70)
    print(" SENTINELAI — AI VERIFICATION TEST")
    print("=" * 70)

    before = FakeProfile(
        overall_score=80,
        overall_level="HIGH",
        findings=[
            FakeFinding("finding-a"),
            FakeFinding("finding-b"),
        ],
    )

    after = FakeProfile(
        overall_score=30,
        overall_level="MEDIUM",
        findings=[
            FakeFinding("finding-b"),
        ],
    )

    service = RiskComparisonService()

    result = service.compare(
        before,
        after,
    )

    print("\n[1] Comparing risk scores...")

    assert result.before_score == 80
    assert result.after_score == 30
    assert result.score_delta == -50

    print("[PASS] Risk score comparison")

    print("\n[2] Detecting resolved findings...")

    assert "finding-a" in (
        result.resolved_findings
    )

    print("[PASS] Resolved finding detection")

    print("\n[3] Detecting remaining findings...")

    assert "finding-b" in (
        result.remaining_findings
    )

    print("[PASS] Remaining finding detection")

    print("\n[4] Verification decision...")

    assert result.improved is True

    print("[PASS] Verification succeeded")

    print()
    print("=" * 70)
    print(" AI VERIFICATION TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_test()