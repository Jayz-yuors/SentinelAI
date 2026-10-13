from ai.security.persistence.neo4j_persistence import (
    Neo4jSecurityPersistence
)


TEST_REPOSITORY = (
    "sentinelai-neo4j-test"
)


def run_test():

    print()
    print("=" * 70)
    print(
        "SENTINELAI — NEO4J SECURITY PERSISTENCE TEST"
    )
    print("=" * 70)

    db = None

    try:

        # ====================================================
        # INITIALIZE
        # ====================================================

        db = Neo4jSecurityPersistence()

        print(
            "\n[TEST] Connecting to Neo4j..."
        )

        assert db.verify_connection() is True

        print(
            "[PASS] Neo4j connection"
        )

        # ====================================================
        # SECURITY FINDING
        # ====================================================

        finding = {

            "id":
                "sentinelai-test-finding-001",

            "repository":
                TEST_REPOSITORY,

            "type":
                "SECRET",

            "category":
                "API_KEY",

            "severity":
                "HIGH",

            "file":
                "config.py",

            "line":
                25,

            "message":
                "Hard-coded API key detected",

            "exploitable":
                True,

            "riskScore":
                8.5
        }

        print(
            "\n[TEST] Saving SecurityFinding..."
        )

        saved_finding = (
            db.save_security_finding(
                finding
            )
        )

        assert (
            saved_finding["id"]
            == finding["id"]
        )

        print(
            "[PASS] SecurityFinding persisted"
        )

        # ====================================================
        # READ FINDING
        # ====================================================

        findings = (
            db.get_security_findings(
                TEST_REPOSITORY
            )
        )

        assert len(findings) == 1

        assert (
            findings[0]["category"]
            == "API_KEY"
        )

        print(
            "[PASS] SecurityFinding read-back"
        )

        # ====================================================
        # THREAT
        # ====================================================

        threat = {

            "id":
                "sentinelai-test-threat-001",

            "repository":
                TEST_REPOSITORY,

            "type":
                "CREDENTIAL_EXPOSURE",

            "severity":
                "HIGH",

            "description":
                "Potential credential exposure",

            "riskScore":
                9.0
        }

        print(
            "\n[TEST] Saving Threat..."
        )

        saved_threat = (
            db.save_threat(
                threat
            )
        )

        assert (
            saved_threat["id"]
            == threat["id"]
        )

        print(
            "[PASS] Threat persisted"
        )

        # ====================================================
        # LINK FINDING TO THREAT
        # ====================================================

        print(
            "\n[TEST] Creating finding → threat relationship..."
        )

        relationship_created = (
            db.link_finding_to_threat(
                finding_id=
                    finding["id"],

                threat_id=
                    threat["id"]
            )
        )

        assert relationship_created is True

        print(
            "[PASS] Finding → Threat relationship"
        )

        # ====================================================
        # READ THREATS
        # ====================================================

        threats = (
            db.get_threats(
                TEST_REPOSITORY
            )
        )

        assert len(threats) == 1

        print(
            "[PASS] Threat read-back"
        )

        # ====================================================
        # FINAL DIRECT CYPHER VERIFICATION
        # ====================================================

        with db.driver.session(
            database="neo4j"
        ) as session:

            result = session.run(
                """
                MATCH (f:SecurityFinding)
                MATCH (t:Threat)

                MATCH (f)-[:CONTRIBUTES_TO]->(t)

                WHERE
                    f.repository =
                        $repository

                RETURN
                    f.id AS findingId,
                    t.id AS threatId
                """,
                {
                    "repository":
                        TEST_REPOSITORY
                }
            )

            record = result.single()

            assert record is not None

            print(
                "[PASS] Neo4j relationship verification"
            )

        # ====================================================
        # SUCCESS
        # ====================================================

        print()
        print("=" * 70)
        print(
            "NEO4J SECURITY PERSISTENCE TEST PASSED"
        )
        print("=" * 70)

    finally:

        # ====================================================
        # CLEANUP
        # ====================================================

        if db:

            print(
                "\n[TEST] Cleaning test data..."
            )

            db.delete_test_data(
                TEST_REPOSITORY
            )

            print(
                "[PASS] Test data cleanup"
            )

            db.close()

            print(
                "[PASS] Neo4j driver closed"
            )


if __name__ == "__main__":

    run_test()