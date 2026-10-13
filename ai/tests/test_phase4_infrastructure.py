from ai.infrastructure.config.settings import (
    APP_NAME,
    POSTGRES_DATABASE,
    NEO4J_DATABASE
)

from ai.database.postgres.connection import (
    get_connection
)

from ai.database.neo4j.connection import (
    verify_connection,
    close_driver
)

from ai.database.postgres.repositories.analysis_repository import (
    initialize_analysis_table,
    save_analysis,
    get_analysis
)


def run_test():

    print()
    print("=" * 75)
    print(
        "SENTINELAI — PHASE 4 INFRASTRUCTURE TEST"
    )
    print("=" * 75)

    # ========================================================
    # CONFIGURATION
    # ========================================================

    assert APP_NAME == "SentinelAI"

    print(
        "[PASS] Configuration loading"
    )

    # ========================================================
    # POSTGRES
    # ========================================================

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT 1;"
    )

    result = cursor.fetchone()

    cursor.close()

    connection.close()

    assert result[0] == 1

    print(
        "[PASS] PostgreSQL connectivity"
    )

    # ========================================================
    # NEO4J
    # ========================================================

    assert verify_connection() is True

    print(
        "[PASS] Neo4j connectivity"
    )

    # ========================================================
    # ANALYSIS TABLE
    # ========================================================

    initialize_analysis_table()

    print(
        "[PASS] Analysis table initialization"
    )

    # ========================================================
    # SAVE / READ
    # ========================================================

    analysis_id = (
        "phase4-test-analysis"
    )

    save_analysis(
        analysis_id,
        "sentinelai-test",
        "sentinelai-test",
        "main",
        "COMPLETED"
    )

    print(
        "[PASS] Analysis persistence"
    )

    record = get_analysis(
        analysis_id
    )

    assert record is not None

    assert (
        record["analysisId"]
        == analysis_id
    )

    print(
        "[PASS] Analysis read-back"
    )

    # ========================================================
    # CLEANUP
    # ========================================================

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM sentinelai_analysis
        WHERE analysis_id = %s;
        """,
        (
            analysis_id,
        )
    )

    connection.commit()

    cursor.close()

    connection.close()

    close_driver()

    print(
        "[PASS] Test cleanup"
    )

    print()
    print(
        "PHASE 4 INFRASTRUCTURE TEST PASSED"
    )
    print("=" * 75)


if __name__ == "__main__":
    run_test()