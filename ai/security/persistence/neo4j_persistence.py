import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# NEO4J CONFIGURATION
# ============================================================

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
# NEO4J PERSISTENCE CLASS
# ============================================================

class Neo4jSecurityPersistence:
    """
    Handles persistence of SentinelAI security findings
    and threats into Neo4j.
    """

    def __init__(self):

        if not NEO4J_PASSWORD:
            raise RuntimeError(
                "NEO4J_PASSWORD is not configured. "
                "Add it to the .env file."
            )

        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(
                NEO4J_USER,
                NEO4J_PASSWORD
            )
        )

    # ========================================================
    # CONNECTION TEST
    # ========================================================

    def verify_connection(self):

        with self.driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                "RETURN 1 AS value"
            )

            record = result.single()

            return record["value"] == 1

    # ========================================================
    # CREATE SECURITY FINDING
    # ========================================================

    def save_security_finding(
        self,
        finding: Dict[str, Any]
    ):

        query = """
        MERGE (f:SecurityFinding {
            id: $id
        })

        SET
            f.repository = $repository,
            f.type = $type,
            f.category = $category,
            f.severity = $severity,
            f.file = $file,
            f.line = $line,
            f.message = $message,
            f.exploitable = $exploitable,
            f.riskScore = $riskScore

        RETURN f
        """

        parameters = {
            "id": str(
                finding.get("id", "")
            ),

            "repository": str(
                finding.get(
                    "repository",
                    ""
                )
            ),

            "type": str(
                finding.get(
                    "type",
                    "SECURITY"
                )
            ),

            "category": str(
                finding.get(
                    "category",
                    "UNKNOWN"
                )
            ),

            "severity": str(
                finding.get(
                    "severity",
                    "LOW"
                )
            ).upper(),

            "file": str(
                finding.get(
                    "file",
                    ""
                )
            ),

            "line": self._safe_int(
                finding.get(
                    "line"
                )
            ),

            "message": str(
                finding.get(
                    "message",
                    ""
                )
            ),

            "exploitable": bool(
                finding.get(
                    "exploitable",
                    False
                )
            ),

            "riskScore": self._safe_float(
                finding.get(
                    "riskScore",
                    0
                )
            )
        }

        with self.driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                query,
                parameters
            )

            record = result.single()

            if record is None:
                raise RuntimeError(
                    "Security finding was not persisted."
                )

            return dict(
                record["f"]
            )

    # ========================================================
    # SAVE MULTIPLE SECURITY FINDINGS
    # ========================================================

    def save_security_findings(
        self,
        findings: List[Dict[str, Any]]
    ):

        saved = []

        for finding in findings:

            saved_finding = (
                self.save_security_finding(
                    finding
                )
            )

            saved.append(
                saved_finding
            )

        return saved

    # ========================================================
    # CREATE THREAT
    # ========================================================

    def save_threat(
        self,
        threat: Dict[str, Any]
    ):

        query = """
        MERGE (t:Threat {
            id: $id
        })

        SET
            t.repository = $repository,
            t.type = $type,
            t.severity = $severity,
            t.description = $description,
            t.riskScore = $riskScore

        RETURN t
        """

        parameters = {
            "id": str(
                threat.get(
                    "id",
                    ""
                )
            ),

            "repository": str(
                threat.get(
                    "repository",
                    ""
                )
            ),

            "type": str(
                threat.get(
                    "type",
                    "UNKNOWN"
                )
            ),

            "severity": str(
                threat.get(
                    "severity",
                    "LOW"
                )
            ).upper(),

            "description": str(
                threat.get(
                    "description",
                    ""
                )
            ),

            "riskScore": self._safe_float(
                threat.get(
                    "riskScore",
                    0
                )
            )
        }

        with self.driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                query,
                parameters
            )

            record = result.single()

            if record is None:
                raise RuntimeError(
                    "Threat was not persisted."
                )

            return dict(
                record["t"]
            )

    # ========================================================
    # LINK FINDING TO THREAT
    # ========================================================

    def link_finding_to_threat(
        self,
        finding_id: str,
        threat_id: str
    ):

        query = """
        MATCH (f:SecurityFinding {
            id: $finding_id
        })

        MATCH (t:Threat {
            id: $threat_id
        })

        MERGE (f)-[:CONTRIBUTES_TO]->(t)

        RETURN f, t
        """

        with self.driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                query,
                {
                    "finding_id": finding_id,
                    "threat_id": threat_id
                }
            )

            record = result.single()

            return record is not None

    # ========================================================
    # GET SECURITY FINDINGS
    # ========================================================

    def get_security_findings(
        self,
        repository: Optional[str] = None
    ):

        if repository:

            query = """
            MATCH (f:SecurityFinding)
            WHERE f.repository = $repository
            RETURN f
            ORDER BY f.riskScore DESC
            """

            parameters = {
                "repository": repository
            }

        else:

            query = """
            MATCH (f:SecurityFinding)
            RETURN f
            ORDER BY f.riskScore DESC
            """

            parameters = {}

        with self.driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                query,
                parameters
            )

            return [
                dict(record["f"])
                for record in result
            ]

    # ========================================================
    # GET THREATS
    # ========================================================

    def get_threats(
        self,
        repository: Optional[str] = None
    ):

        if repository:

            query = """
            MATCH (t:Threat)
            WHERE t.repository = $repository
            RETURN t
            ORDER BY t.riskScore DESC
            """

            parameters = {
                "repository": repository
            }

        else:

            query = """
            MATCH (t:Threat)
            RETURN t
            ORDER BY t.riskScore DESC
            """

            parameters = {}

        with self.driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                query,
                parameters
            )

            return [
                dict(record["t"])
                for record in result
            ]

    # ========================================================
    # DELETE TEST DATA
    # ========================================================

    def delete_test_data(
        self,
        repository: str
    ):

        query = """
        MATCH (f:SecurityFinding {
            repository: $repository
        })
        DETACH DELETE f

        WITH 1 AS dummy

        MATCH (t:Threat {
            repository: $repository
        })
        DETACH DELETE t

        RETURN dummy
        """

        with self.driver.session(
            database=NEO4J_DATABASE
        ) as session:

            session.run(
                query,
                {
                    "repository": repository
                }
            )

    # ========================================================
    # CLOSE DRIVER
    # ========================================================

    def close(self):

        if self.driver:

            self.driver.close()

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _safe_int(
        value
    ):

        if value is None:
            return 0

        try:
            return int(value)

        except (
            TypeError,
            ValueError
        ):
            return 0

    @staticmethod
    def _safe_float(
        value
    ):

        if value is None:
            return 0.0

        try:
            return float(value)

        except (
            TypeError,
            ValueError
        ):
            return 0.0