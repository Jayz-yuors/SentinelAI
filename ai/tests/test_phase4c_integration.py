from ai.pipeline.pipeline_service import (
    execute_pipeline
)

from ai.database.postgres.repositories.analysis_repository import (
    get_analysis,
    delete_analysis,
)

from ai.database.neo4j.analysis_graph_repository import (
    get_analysis_graph
)

from ai.database.neo4j.connection import (
    close_driver
)


TEST_REPOSITORY = (
    "https://github.com/psf/requests.git"
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

    print()
    print(
        "SENTINELAI — PHASE 4C COMPLETE INTEGRATION TEST"
    )
    print()

    # -------------------------------------------------
    # Execute complete pipeline
    # -------------------------------------------------

    response = execute_pipeline(
        TEST_REPOSITORY,
        "main"
    )

    check(
        "analysisId" in response,
        "Analysis ID generated"
    )

    analysis_id = response[
        "analysisId"
    ]

    check(
        response["success"],
        "Complete analysis pipeline execution"
    )

    check(
        response["status"] == "COMPLETED",
        "Pipeline completed"
    )

    result = response.get(
        "result",
        {}
    )

    # -------------------------------------------------
    # Phase 1
    # -------------------------------------------------

    check(
        "phase1" in result,
        "Phase 1 unified result"
    )

    check(
        "totalFiles" in result,
        "Phase 1 repository analysis"
    )

    # -------------------------------------------------
    # Phase 2
    # -------------------------------------------------

    check(
        "phase2" in result,
        "Phase 2 unified result"
    )

    check(
        "dependencyGraph" in result,
        "Phase 2 dependency graph"
    )

    # -------------------------------------------------
    # Phase 3
    # -------------------------------------------------

    check(
        "phase3" in result,
        "Phase 3 unified result"
    )

    check(
        "securityAnalysis" in result,
        "Phase 3 security analysis"
    )

    # -------------------------------------------------
    # PostgreSQL
    # -------------------------------------------------

    stored = get_analysis(
        analysis_id
    )

    check(
        stored is not None,
        "Analysis stored in PostgreSQL"
    )

    check(
        stored["status"] == "COMPLETED",
        "PostgreSQL analysis status"
    )

    check(
        stored["phase1"] is not None,
        "PostgreSQL Phase 1 persistence"
    )

    check(
        stored["phase2"] is not None,
        "PostgreSQL Phase 2 persistence"
    )

    check(
        stored["phase3"] is not None,
        "PostgreSQL Phase 3 persistence"
    )

    check(
        stored["result"] is not None,
        "PostgreSQL unified result persistence"
    )

    # -------------------------------------------------
    # Neo4j
    # -------------------------------------------------

    graph = get_analysis_graph(
        analysis_id
    )

    check(
        graph is not None,
        "Neo4j analysis graph persistence"
    )

    check(
        graph["analysis"] is not None,
        "Neo4j analysis node"
    )

    # -------------------------------------------------
    # Cleanup
    # -------------------------------------------------

    delete_analysis(
        analysis_id
    )

    close_driver()

    print()
    print(
        "PHASE 4C COMPLETE INTEGRATION PASSED"
    )


if __name__ == "__main__":
    run_test()