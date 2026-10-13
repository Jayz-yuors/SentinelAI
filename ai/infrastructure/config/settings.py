from pathlib import Path
import os


# SentinelAI/
# └── .env
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


def load_env_file():
    """
    Lightweight .env loader.

    Existing environment variables take priority.
    """

    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = value.strip()

        if (
            len(value) >= 2
            and value[0] == '"'
            and value[-1] == '"'
        ):
            value = value[1:-1]

        if (
            len(value) >= 2
            and value[0] == "'"
            and value[-1] == "'"
        ):
            value = value[1:-1]

        os.environ.setdefault(key, value)


load_env_file()


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

APP_NAME = os.getenv(
    "APP_NAME",
    "SentinelAI AI Service"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

APP_ENV = os.getenv(
    "APP_ENV",
    "development"
)

APP_HOST = os.getenv(
    "APP_HOST",
    "127.0.0.1"
)

APP_PORT = int(
    os.getenv(
        "APP_PORT",
        "8000"
    )
)


# ---------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------

POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost"
)

POSTGRES_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5432"
    )
)

POSTGRES_DATABASE = os.getenv(
    "POSTGRES_DATABASE",
    "DemoDb"
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "postgres"
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "JayK@123!"
)


# ---------------------------------------------------------
# Neo4j
# ---------------------------------------------------------

NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://localhost:7687"
)

NEO4J_USER = os.getenv(
    "NEO4J_USER",
    "neo4j"
)

NEO4J_PASSWORD = os.getenv(
    "NEO4J_PASSWORD",
    "JayK@123!"
)

NEO4J_DATABASE = os.getenv(
    "NEO4J_DATABASE",
    "neo4j"
)


# ---------------------------------------------------------
# Pipeline
# ---------------------------------------------------------

PIPELINE_MAX_RETRIES = int(
    os.getenv(
        "PIPELINE_MAX_RETRIES",
        "2"
    )
)

PIPELINE_TIMEOUT_SECONDS = int(
    os.getenv(
        "PIPELINE_TIMEOUT_SECONDS",
        "900"
    )
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)


def get_postgres_config():
    return {
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
        "database": POSTGRES_DATABASE,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
    }


def get_neo4j_config():
    return {
        "uri": NEO4J_URI,
        "user": NEO4J_USER,
        "password": NEO4J_PASSWORD,
        "database": NEO4J_DATABASE,
    }