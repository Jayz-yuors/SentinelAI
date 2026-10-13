from ai.database.postgres.connection import (
    check_postgres
)

from ai.database.neo4j.connection import (
    verify_connection
)

from ai.infrastructure.config.settings import (
    APP_NAME,
    APP_VERSION,
)


def application_health():

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "UP",
    }


def postgres_health():

    healthy = check_postgres()

    return {
        "service": "postgresql",
        "status": (
            "UP"
            if healthy
            else "DOWN"
        ),
    }


def neo4j_health():

    healthy = verify_connection()

    return {
        "service": "neo4j",
        "status": (
            "UP"
            if healthy
            else "DOWN"
        ),
    }


def ai_service_health():

    return {
        "service": "ai-analysis-engine",
        "status": "UP",
    }


def complete_health():

    postgres = postgres_health()
    neo4j = neo4j_health()
    ai = ai_service_health()

    services = [
        postgres,
        neo4j,
        ai,
    ]

    overall = (
        "UP"
        if all(
            item["status"] == "UP"
            for item in services
        )
        else "DEGRADED"
    )

    return {
        "status": overall,
        "application": application_health(),
        "services": {
            "postgresql": postgres,
            "neo4j": neo4j,
            "ai": ai,
        },
    }