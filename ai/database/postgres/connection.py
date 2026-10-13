import os
from contextlib import contextmanager

import psycopg2

from ai.infrastructure.config.settings import (
    get_postgres_config
)

from ai.infrastructure.exceptions.exceptions import (
    DatabaseException
)


def _get_effective_postgres_config():
    """
    Preserve the existing PostgreSQL configuration while allowing
    Docker/environment variables to override connection settings.

    Existing local configuration remains the fallback.
    """

    config = dict(get_postgres_config())

    # ---------------------------------------------------------
    # Environment overrides
    # ---------------------------------------------------------

    host = os.getenv("SENTINELAI_POSTGRES_HOST")
    port = os.getenv("SENTINELAI_POSTGRES_PORT")
    database = os.getenv("SENTINELAI_POSTGRES_DB")
    username = os.getenv("SENTINELAI_POSTGRES_USER")
    password = os.getenv("SENTINELAI_POSTGRES_PASSWORD")

    if host:
        config["host"] = host

    if port:
        config["port"] = int(port)

    if database:
        # Support either common naming convention without
        # breaking the existing settings implementation.
        if "dbname" in config:
            config["dbname"] = database
        elif "database" in config:
            config["database"] = database
        else:
            config["dbname"] = database

    if username:
        if "user" in config:
            config["user"] = username
        elif "username" in config:
            config["username"] = username
        else:
            config["user"] = username

    if password:
        config["password"] = password

    return config


def get_connection():

    try:

        return psycopg2.connect(
            **_get_effective_postgres_config()
        )

    except Exception as exc:

        config = _get_effective_postgres_config()

        raise DatabaseException(
            (
                "PostgreSQL connection failed: "
                f"host={config.get('host', 'unknown')}, "
                f"port={config.get('port', 'unknown')}, "
                f"database={config.get('dbname', config.get('database', 'unknown'))}, "
                f"error={exc}"
            ),
            "POSTGRES_CONNECTION_ERROR"
        ) from exc


@contextmanager
def database_transaction():

    connection = None

    try:

        connection = get_connection()

        yield connection

        connection.commit()

    except Exception as exc:

        if connection:
            connection.rollback()

        if isinstance(
            exc,
            DatabaseException
        ):
            raise

        raise DatabaseException(
            f"Database transaction failed: {exc}",
            "POSTGRES_TRANSACTION_ERROR"
        ) from exc

    finally:

        if connection:
            connection.close()


def check_postgres():

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT 1"
            )

            result = cursor.fetchone()

        return result == (1,)

    except Exception:

        return False

    finally:

        if connection:
            connection.close()