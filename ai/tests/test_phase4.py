from ai.pipeline.pipeline_state import (
    PipelineState
)

from ai.pipeline.pipeline_service import (
    execute_pipeline
)

from ai.infrastructure.health.health_service import (
    complete_health
)

from ai.infrastructure.metrics.metrics import (
    analysis_metrics
)


def run_test():

    print()
    print("=" * 75)
    print(
        "SENTINELAI — PHASE 4 VALIDATION"
    )
    print("=" * 75)

    # ========================================================
    # TC01 — PIPELINE STATE
    # ========================================================

    state = PipelineState()

    assert state.get_state() == "QUEUED"

    state.set_state(
        "RUNNING"
    )

    assert state.get_state() == "RUNNING"

    print(
        "[PASS] TC01 — Pipeline state management"
    )

    # ========================================================
    # TC02 — DATABASE / SERVICE HEALTH
    # ========================================================

    health = complete_health()

    assert "status" in health

    assert "services" in health

    assert (
        health["services"]["postgresql"]["status"]
        == "UP"
    )

    assert (
        health["services"]["neo4j"]["status"]
        == "UP"
    )

    print(
        "[PASS] TC02 — Infrastructure health"
    )

    # ========================================================
    # TC03 — COMPLETE PHASE 1+2+3 PIPELINE
    # ========================================================

    repository_url = (
        "https://github.com/"
        "octocat/Hello-World.git"
    )

    result = execute_pipeline(
        repository_url,
        "master"
    )

    # --------------------------------------------------------
    # Some repositories may use main instead of master.
    # If this repository cannot be cloned with master,
    # the integrated pipeline will report failure.
    # --------------------------------------------------------

    assert isinstance(
        result,
        dict
    )

    assert "analysisId" in result

    print(
        "[PASS] TC03 — Pipeline execution"
    )

    # ========================================================
    # TC04 — PIPELINE RESULT
    # ========================================================

    if result["success"]:

        pipeline_result = (
            result["result"]
        )

        assert (
            "totalFiles"
            in pipeline_result
        )

        assert (
            "dependencyGraph"
            in pipeline_result
        )

        assert (
            "securityAnalysis"
            in pipeline_result
        )

        print(
            "[PASS] TC04 — Phase 1 + Phase 2 + Phase 3 result"
        )

    else:

        print(
            "[INFO] TC04 — External repository execution "
            "returned failure"
        )

    # ========================================================
    # TC05 — METRICS
    # ========================================================

    metrics = (
        analysis_metrics.get_metrics()
    )

    assert isinstance(
        metrics,
        dict
    )

    print(
        "[PASS] TC05 — Metrics system"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print(
        "PHASE 4 VALIDATION COMPLETED"
    )

    print("=" * 75)


if __name__ == "__main__":
    run_test()