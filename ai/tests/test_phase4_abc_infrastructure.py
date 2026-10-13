from ai.database.postgres.connection import (
    check_postgres
)

from ai.database.neo4j.connection import (
    verify_connection,
    close_driver
)

from ai.database.postgres.repositories.analysis_repository import (
    initialize_analysis_table,
    save_analysis,
    update_analysis_status,
    save_phase_result,
    save_unified_result,
    get_analysis,
    delete_analysis,
)

from ai.infrastructure.health.health_service import (
    complete_health
)

from ai.infrastructure.metrics.metrics import (
    analysis_metrics
)


def check(
    condition,
    message
):

    if not condition:
        raise AssertionError(message)

    print(
        f"[PASS] {message}"
    )


def run_test():

    analysis_id = (
        "phase4abc-test-analysis"
    )

    print()
    print(
        "SENTINELAI — PHASE 4A + 4B INFRASTRUCTURE TEST"
    )
    print()

    # -------------------------------------------------
    # PostgreSQL
    # -------------------------------------------------

    check(
        check_postgres(),
        "PostgreSQL connectivity"
    )

    initialize_analysis_table()

    check(
        True,
        "Analysis table initialization"
    )

    # -------------------------------------------------
    # Save analysis
    # -------------------------------------------------

    save_analysis(
        analysis_id=analysis_id,
        repository_url=(
            "https://github.com/test/repository.git"
        ),
        repository_name="repository",
        branch="main",
        status="RUNNING",
    )

    check(
        get_analysis(analysis_id)
        is not None,
        "Analysis persistence"
    )

    # -------------------------------------------------
    # Phase persistence
    # -------------------------------------------------

    save_phase_result(
        analysis_id,
        1,
        {
            "totalFiles": 10,
            "languages": ["Python"],
        }
    )

    save_phase_result(
        analysis_id,
        2,
        {
            "dependencyGraph": {
                "nodes": [],
                "edges": [],
            }
        }
    )

    save_phase_result(
        analysis_id,
        3,
        {
            "securityAnalysis": {
                "findings": []
            }
        }
    )

    save_unified_result(
        analysis_id,
        {
            "analysisId": analysis_id,
            "status": "COMPLETED",
        }
    )

    update_analysis_status(
        analysis_id,
        "COMPLETED"
    )

    stored = get_analysis(
        analysis_id
    )

    check(
        stored["phase1"] is not None,
        "Phase 1 result persistence"
    )

    check(
        stored["phase2"] is not None,
        "Phase 2 result persistence"
    )

    check(
        stored["phase3"] is not None,
        "Phase 3 result persistence"
    )

    check(
        stored["result"] is not None,
        "Unified result persistence"
    )

    # -------------------------------------------------
    # Neo4j
    # -------------------------------------------------

    check(
        verify_connection(),
        "Neo4j connectivity"
    )

    # -------------------------------------------------
    # Health
    # -------------------------------------------------

    health = complete_health()

    check(
        "status" in health,
        "Complete infrastructure health"
    )

    # -------------------------------------------------
    # Metrics
    # -------------------------------------------------

    metrics = analysis_metrics.snapshot()

    check(
        "total" in metrics,
        "Metrics system"
    )

    # -------------------------------------------------
    # Cleanup
    # -------------------------------------------------

    check(
        delete_analysis(analysis_id),
        "Test cleanup"
    )

    close_driver()

    print()
    print(
        "PHASE 4A + 4B INFRASTRUCTURE TEST PASSED"
    )


if __name__ == "__main__":
    run_test()