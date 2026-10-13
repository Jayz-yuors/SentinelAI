from neo4j import GraphDatabase

from ai.infrastructure.config.settings import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    NEO4J_DATABASE,
)

from ai.infrastructure.exceptions.exceptions import (
    Neo4jException
)


_driver = None


def get_driver():

    global _driver

    if _driver is None:

        try:

            _driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(
                    NEO4J_USER,
                    NEO4J_PASSWORD
                )
            )

        except Exception as exc:

            raise Neo4jException(
                f"Neo4j driver initialization failed: {exc}",
                "NEO4J_DRIVER_ERROR"
            ) from exc

    return _driver


def verify_connection():

    try:

        driver = get_driver()

        driver.verify_connectivity()

        return True

    except Exception:

        return False


def get_session():

    try:

        return get_driver().session(
            database=NEO4J_DATABASE
        )

    except Exception as exc:

        raise Neo4jException(
            f"Neo4j session creation failed: {exc}",
            "NEO4J_SESSION_ERROR"
        ) from exc


def close_driver():

    global _driver

    if _driver:

        _driver.close()
        _driver = None