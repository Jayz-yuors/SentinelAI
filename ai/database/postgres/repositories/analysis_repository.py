import json
from datetime import datetime
from typing import Optional

from ai.database.postgres.connection import (
    database_transaction
)


def initialize_analysis_table():
    """
    Create the analysis table if it does not exist.

    Also performs backward-compatible schema migration
    for databases created using an older SentinelAI version.
    """

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            # ---------------------------------------------------------
            # CREATE BASE TABLE
            # ---------------------------------------------------------

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sentinelai_analysis (
                    analysis_id VARCHAR(100) PRIMARY KEY,
                    repository_url TEXT NOT NULL,
                    repository_name VARCHAR(255) NOT NULL,
                    branch VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL,

                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP NULL
                )
                """
            )

            # ---------------------------------------------------------
            # BACKWARD-COMPATIBLE MIGRATION
            # ---------------------------------------------------------
            #
            # These columns are added only if they do not already exist.
            # Existing analysis records are preserved.
            #

            cursor.execute(
                """
                ALTER TABLE sentinelai_analysis
                ADD COLUMN IF NOT EXISTS error_message TEXT NULL
                """
            )

            cursor.execute(
                """
                ALTER TABLE sentinelai_analysis
                ADD COLUMN IF NOT EXISTS phase1_result JSONB NULL
                """
            )

            cursor.execute(
                """
                ALTER TABLE sentinelai_analysis
                ADD COLUMN IF NOT EXISTS phase2_result JSONB NULL
                """
            )

            cursor.execute(
                """
                ALTER TABLE sentinelai_analysis
                ADD COLUMN IF NOT EXISTS phase3_result JSONB NULL
                """
            )

            cursor.execute(
                """
                ALTER TABLE sentinelai_analysis
                ADD COLUMN IF NOT EXISTS unified_result JSONB NULL
                """
            )


def save_analysis(
    analysis_id: str,
    repository_url: str,
    repository_name: str,
    branch: str,
    status: str
):
    """
    Create or update an analysis session.
    """

    initialize_analysis_table()

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO sentinelai_analysis (
                    analysis_id,
                    repository_url,
                    repository_name,
                    branch,
                    status,
                    created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (analysis_id)
                DO UPDATE SET
                    repository_url = EXCLUDED.repository_url,
                    repository_name = EXCLUDED.repository_name,
                    branch = EXCLUDED.branch,
                    status = EXCLUDED.status
                """,
                (
                    analysis_id,
                    repository_url,
                    repository_name,
                    branch,
                    status,
                    datetime.utcnow(),
                )
            )


def update_analysis_status(
    analysis_id: str,
    status: str,
    error_message: Optional[str] = None
):
    """
    Update analysis execution status.
    """

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            completed_at = (
                datetime.utcnow()
                if status in {
                    "COMPLETED",
                    "FAILED",
                    "TIMEOUT"
                }
                else None
            )

            cursor.execute(
                """
                UPDATE sentinelai_analysis
                SET
                    status = %s,
                    completed_at = COALESCE(
                        %s,
                        completed_at
                    ),
                    error_message = %s
                WHERE analysis_id = %s
                """,
                (
                    status,
                    completed_at,
                    error_message,
                    analysis_id,
                )
            )


def save_phase_result(
    analysis_id: str,
    phase: int,
    result: dict
):
    """
    Persist an individual phase result.
    """

    column = {
        1: "phase1_result",
        2: "phase2_result",
        3: "phase3_result",
    }.get(phase)

    if column is None:
        raise ValueError(
            f"Unsupported phase: {phase}"
        )

    payload = json.dumps(
        result,
        default=str
    )

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                f"""
                UPDATE sentinelai_analysis
                SET {column} = %s::jsonb
                WHERE analysis_id = %s
                """,
                (
                    payload,
                    analysis_id
                )
            )


def save_unified_result(
    analysis_id: str,
    result: dict
):
    """
    Persist the final unified analysis result.
    """

    payload = json.dumps(
        result,
        default=str
    )

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE sentinelai_analysis
                SET unified_result = %s::jsonb
                WHERE analysis_id = %s
                """,
                (
                    payload,
                    analysis_id
                )
            )


def get_analysis(
    analysis_id: str
):
    """
    Retrieve a complete analysis record.
    """

    initialize_analysis_table()

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    analysis_id,
                    repository_url,
                    repository_name,
                    branch,
                    status,
                    created_at,
                    completed_at,
                    error_message,
                    phase1_result,
                    phase2_result,
                    phase3_result,
                    unified_result
                FROM sentinelai_analysis
                WHERE analysis_id = %s
                """,
                (analysis_id,)
            )

            row = cursor.fetchone()

    if not row:
        return None

    return {
        "analysisId": row[0],
        "repositoryUrl": row[1],
        "repositoryName": row[2],
        "branch": row[3],
        "status": row[4],
        "createdAt": (
            row[5].isoformat()
            if row[5]
            else None
        ),
        "completedAt": (
            row[6].isoformat()
            if row[6]
            else None
        ),
        "errorMessage": row[7],
        "phase1": row[8],
        "phase2": row[9],
        "phase3": row[10],
        "result": row[11],
    }


def list_analyses(
    repository_url: Optional[str] = None,
    limit: int = 20
):
    """
    Retrieve analysis history.
    """

    initialize_analysis_table()

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            if repository_url:

                cursor.execute(
                    """
                    SELECT
                        analysis_id,
                        repository_url,
                        repository_name,
                        branch,
                        status,
                        created_at,
                        completed_at
                    FROM sentinelai_analysis
                    WHERE repository_url = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (
                        repository_url,
                        limit
                    )
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        analysis_id,
                        repository_url,
                        repository_name,
                        branch,
                        status,
                        created_at,
                        completed_at
                    FROM sentinelai_analysis
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )

            rows = cursor.fetchall()

    return [
        {
            "analysisId": row[0],
            "repositoryUrl": row[1],
            "repositoryName": row[2],
            "branch": row[3],
            "status": row[4],
            "createdAt": (
                row[5].isoformat()
                if row[5]
                else None
            ),
            "completedAt": (
                row[6].isoformat()
                if row[6]
                else None
            ),
        }
        for row in rows
    ]


def delete_analysis(
    analysis_id: str
):
    """
    Delete an analysis record.
    """

    with database_transaction() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM sentinelai_analysis
                WHERE analysis_id = %s
                """,
                (analysis_id,)
            )

            return cursor.rowcount > 0