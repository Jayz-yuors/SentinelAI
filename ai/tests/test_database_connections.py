import os
import sys

# ============================================================
# OPTIONAL .env SUPPORT
# ============================================================

try:
    from dotenv import load_dotenv

    load_dotenv()

except ImportError:
    pass


# ============================================================
# DATABASE IMPORTS
# ============================================================

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None


# ============================================================
# CONFIGURATION
# ============================================================

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

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "DemoDb"
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "postgres"
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD"
)


NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://localhost:7687"
)

NEO4J_USER = os.getenv(
    "NEO4J_USER",
    "neo4j"
)

NEO4J_PASSWORD = os.getenv(
    "NEO4J_PASSWORD"
)

NEO4J_DATABASE = os.getenv(
    "NEO4J_DATABASE",
    "neo4j"
)


# ============================================================
# RESULT HELPERS
# ============================================================

postgres_passed = False
neo4j_passed = False


def print_pass(message):

    print(
        f"[PASS] {message}"
    )


def print_fail(message):

    print(
        f"[FAIL] {message}"
    )


# ============================================================
# POSTGRESQL TEST
# ============================================================

def test_postgresql():

    global postgres_passed

    print()
    print("=" * 70)
    print("POSTGRESQL DATABASE TEST")
    print("=" * 70)

    if psycopg2 is None:

        print_fail(
            "psycopg2 is not installed"
        )

        print(
            "Install using:"
        )

        print(
            "pip install psycopg2-binary"
        )

        return

    if not POSTGRES_PASSWORD:

        print_fail(
            "POSTGRES_PASSWORD environment variable is not set"
        )

        print()
        print(
            "Set your PostgreSQL password before running the test."
        )

        return

    connection = None

    try:

        # ----------------------------------------------------
        # 1. Connection
        # ----------------------------------------------------

        print(
            f"Connecting to PostgreSQL:"
        )

        print(
            f"  Host     : {POSTGRES_HOST}"
        )

        print(
            f"  Port     : {POSTGRES_PORT}"
        )

        print(
            f"  Database : {POSTGRES_DB}"
        )

        print(
            f"  User     : {POSTGRES_USER}"
        )

        connection = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )

        print_pass(
            "PostgreSQL connection"
        )

        # ----------------------------------------------------
        # 2. Basic query
        # ----------------------------------------------------

        cursor = connection.cursor()

        cursor.execute(
            "SELECT 1;"
        )

        result = cursor.fetchone()

        assert result[0] == 1

        print_pass(
            "PostgreSQL query execution"
        )

        # ----------------------------------------------------
        # 3. Database information
        # ----------------------------------------------------

        cursor.execute(
            "SELECT current_database();"
        )

        current_database = (
            cursor.fetchone()[0]
        )

        print_pass(
            f"Connected database: {current_database}"
        )

        # ----------------------------------------------------
        # 4. PostgreSQL version
        # ----------------------------------------------------

        cursor.execute(
            "SELECT version();"
        )

        version = cursor.fetchone()[0]

        print_pass(
            "PostgreSQL version query"
        )

        print()
        print(
            "PostgreSQL:"
        )

        print(
            f"  {version.split(',')[0]}"
        )

        # ----------------------------------------------------
        # 5. Check Phase 2 tables
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
        )

        tables = [
            row[0]
            for row in cursor.fetchall()
        ]

        print()
        print(
            "Public tables:"
        )

        if tables:

            for table in tables:

                print(
                    f"  - {table}"
                )

        else:

            print(
                "  No tables found"
            )

        expected_tables = {
            "dependencies",
            "security_findings"
        }

        found_expected = (
            expected_tables
            .intersection(set(tables))
        )

        print()

        if found_expected:

            for table in sorted(found_expected):

                print_pass(
                    f"Phase 2 table exists: {table}"
                )

        else:

            print(
                "[INFO] Phase 2 tables "
                "dependencies/security_findings "
                "are not present yet."
            )

            print(
                "[INFO] This means the PostgreSQL "
                "schema files may still need to be executed."
            )

        # ----------------------------------------------------
        # 6. Safe temporary write/read test
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TEMP TABLE sentinelai_db_test (
                id INTEGER,
                message TEXT
            );
            """
        )

        cursor.execute(
            """
            INSERT INTO sentinelai_db_test
            (id, message)
            VALUES
            (1, 'SentinelAI PostgreSQL test');
            """
        )

        cursor.execute(
            """
            SELECT message
            FROM sentinelai_db_test
            WHERE id = 1;
            """
        )

        test_message = cursor.fetchone()[0]

        assert (
            test_message
            == "SentinelAI PostgreSQL test"
        )

        print_pass(
            "PostgreSQL temporary write/read"
        )

        # ----------------------------------------------------
        # 7. Rollback
        # ----------------------------------------------------

        connection.rollback()

        print_pass(
            "PostgreSQL test cleanup"
        )

        cursor.close()

        connection.close()

        postgres_passed = True

    except Exception as error:

        print_fail(
            "PostgreSQL test failed"
        )

        print()
        print(
            f"Error: {error}"
        )

        if connection:

            try:
                connection.close()
            except Exception:
                pass


# ============================================================
# NEO4J TEST
# ============================================================

def test_neo4j():

    global neo4j_passed

    print()
    print("=" * 70)
    print("NEO4J DATABASE TEST")
    print("=" * 70)

    if GraphDatabase is None:

        print_fail(
            "neo4j Python driver is not installed"
        )

        print(
            "Install using:"
        )

        print(
            "pip install neo4j"
        )

        return

    if not NEO4J_PASSWORD:

        print_fail(
            "NEO4J_PASSWORD environment variable is not set"
        )

        print()
        print(
            "Set the password of your Neo4j instance."
        )

        return

    driver = None

    try:

        # ----------------------------------------------------
        # 1. Driver
        # ----------------------------------------------------

        print(
            "Connecting to Neo4j:"
        )

        print(
            f"  URI      : {NEO4J_URI}"
        )

        print(
            f"  Database : {NEO4J_DATABASE}"
        )

        print(
            f"  User     : {NEO4J_USER}"
        )

        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(
                NEO4J_USER,
                NEO4J_PASSWORD
            )
        )

        # ----------------------------------------------------
        # 2. Connectivity
        # ----------------------------------------------------

        driver.verify_connectivity()

        print_pass(
            "Neo4j connection"
        )

        # ----------------------------------------------------
        # 3. Basic Cypher query
        # ----------------------------------------------------

        with driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                "RETURN 1 AS test"
            )

            value = result.single()["test"]

            assert value == 1

            print_pass(
                "Neo4j Cypher execution"
            )

            # ------------------------------------------------
            # 4. Database information
            # ------------------------------------------------

            result = session.run(
                "CALL dbms.components() "
                "YIELD name, versions "
                "RETURN name, versions"
            )

            record = result.single()

            if record:

                print_pass(
                    "Neo4j database information query"
                )

                print()
                print(
                    "Neo4j:"
                )

                print(
                    f"  Name    : {record['name']}"
                )

                print(
                    f"  Version : {record['versions'][0]}"
                )

            # ------------------------------------------------
            # 5. Create temporary SentinelAI test node
            # ------------------------------------------------

            session.run(
                """
                CREATE (n:SentinelAITest {
                    name: 'SentinelAI_DB_TEST'
                })
                """
            ).consume()

            print_pass(
                "Neo4j node creation"
            )

            # ------------------------------------------------
            # 6. Create temporary relationship
            # ------------------------------------------------

            session.run(
                """
                MATCH (a:SentinelAITest {
                    name: 'SentinelAI_DB_TEST'
                })

                CREATE (b:SentinelAITest {
                    name: 'SentinelAI_DB_TEST_TARGET'
                })

                CREATE (a)-[:TEST_DEPENDS_ON]->(b)
                """
            ).consume()

            print_pass(
                "Neo4j relationship creation"
            )

            # ------------------------------------------------
            # 7. Read graph data
            # ------------------------------------------------

            result = session.run(
                """
                MATCH (a:SentinelAITest)
                -[:TEST_DEPENDS_ON]->
                (b:SentinelAITest)

                RETURN a.name AS source,
                       b.name AS target
                """
            )

            record = result.single()

            assert record is not None

            assert (
                record["source"]
                == "SentinelAI_DB_TEST"
            )

            assert (
                record["target"]
                == "SentinelAI_DB_TEST_TARGET"
            )

            print_pass(
                "Neo4j node/relationship read-back"
            )

            # ------------------------------------------------
            # 8. Cleanup
            # ------------------------------------------------

            session.run(
                """
                MATCH (n:SentinelAITest)
                DETACH DELETE n
                """
            ).consume()

            print_pass(
                "Neo4j test cleanup"
            )

        driver.close()

        neo4j_passed = True

    except Exception as error:

        print_fail(
            "Neo4j test failed"
        )

        print()
        print(
            f"Error: {error}"
        )

        if driver:

            try:
                driver.close()
            except Exception:
                pass


# ============================================================
# FINAL RESULT
# ============================================================

def run_tests():

    print()
    print("=" * 70)
    print("SENTINELAI — DATABASE & NEO4J CONNECTIVITY TEST")
    print("=" * 70)

    test_postgresql()

    test_neo4j()

    print()
    print("=" * 70)
    print("FINAL DATABASE TEST RESULT")
    print("=" * 70)

    if postgres_passed:

        print(
            "[PASS] PostgreSQL is operational"
        )

    else:

        print(
            "[FAIL] PostgreSQL requires attention"
        )

    if neo4j_passed:

        print(
            "[PASS] Neo4j is operational"
        )

    else:

        print(
            "[FAIL] Neo4j requires attention"
        )

    print()

    if postgres_passed and neo4j_passed:

        print(
            "DATABASE INFRASTRUCTURE TEST PASSED"
        )

        print(
            "PostgreSQL + Neo4j are reachable "
            "and executable."
        )

        print("=" * 70)

        return 0

    print(
        "DATABASE INFRASTRUCTURE TEST FAILED"
    )

    print(
        "Fix the failed component before "
        "continuing integration."
    )

    print("=" * 70)

    return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(
        run_tests()
    )