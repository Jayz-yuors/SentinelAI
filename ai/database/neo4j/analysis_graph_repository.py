from ai.database.neo4j.connection import (
    get_session
)


def save_analysis_graph(
    analysis_id: str,
    repository_url: str,
    repository_name: str,
    result: dict
):

    session = get_session()

    try:

        session.run(
            """
            MERGE (a:Analysis {
                analysisId: $analysis_id
            })

            SET
                a.repositoryUrl = $repository_url,
                a.repositoryName = $repository_name,
                a.status = $status

            MERGE (r:Repository {
                url: $repository_url
            })

            SET r.name = $repository_name

            MERGE (a)-[:ANALYZES]->(r)
            """,
            analysis_id=analysis_id,
            repository_url=repository_url,
            repository_name=repository_name,
            status=result.get(
                "status",
                "COMPLETED"
            )
        )

        dependency_graph = result.get(
            "dependencyGraph",
            {}
        )

        nodes = dependency_graph.get(
            "nodes",
            []
        )

        edges = dependency_graph.get(
            "edges",
            []
        )

        for node in nodes:

            if isinstance(node, dict):

                node_id = (
                    node.get("id")
                    or node.get("name")
                )

            else:

                node_id = str(node)

            if not node_id:
                continue

            session.run(
                """
                MERGE (d:Dependency {
                    id: $node_id
                })

                WITH d

                MATCH (a:Analysis {
                    analysisId: $analysis_id
                })

                MERGE (a)-[:DISCOVERED]->(d)
                """,
                node_id=str(node_id),
                analysis_id=analysis_id
            )

        for edge in edges:

            if not isinstance(edge, dict):
                continue

            source = (
                edge.get("source")
                or edge.get("from")
            )

            target = (
                edge.get("target")
                or edge.get("to")
            )

            if not source or not target:
                continue

            session.run(
                """
                MATCH (s:Dependency {id: $source})
                MATCH (t:Dependency {id: $target})

                MERGE (s)-[:DEPENDS_ON]->(t)
                """,
                source=str(source),
                target=str(target)
            )

        findings = (
            result
            .get("securityAnalysis", {})
            .get("findings", [])
        )

        for finding in findings:

            if not isinstance(finding, dict):
                continue

            finding_id = (
                finding.get("id")
                or finding.get("findingId")
            )

            if not finding_id:
                finding_id = (
                    f"{analysis_id}-"
                    f"{finding.get('category', 'finding')}-"
                    f"{finding.get('file', 'unknown')}"
                )

            session.run(
                """
                MERGE (f:SecurityFinding {
                    id: $finding_id
                })

                SET
                    f.analysisId = $analysis_id,
                    f.category = $category,
                    f.severity = $severity,
                    f.file = $file,
                    f.message = $message

                WITH f

                MATCH (a:Analysis {
                    analysisId: $analysis_id
                })

                MERGE (a)-[:HAS_FINDING]->(f)
                """,
                finding_id=str(finding_id),
                analysis_id=analysis_id,
                category=str(
                    finding.get(
                        "category",
                        "UNKNOWN"
                    )
                ),
                severity=str(
                    finding.get(
                        "severity",
                        "UNKNOWN"
                    )
                ),
                file=str(
                    finding.get(
                        "file",
                        ""
                    )
                ),
                message=str(
                    finding.get(
                        "message",
                        ""
                    )
                )
            )

    finally:

        session.close()


def get_analysis_graph(
    analysis_id: str
):

    session = get_session()

    try:

        result = session.run(
            """
            MATCH (a:Analysis {
                analysisId: $analysis_id
            })

            OPTIONAL MATCH
                (a)-[:DISCOVERED]->(d:Dependency)

            OPTIONAL MATCH
                (a)-[:HAS_FINDING]->(f:SecurityFinding)

            RETURN
                a,
                collect(DISTINCT d) AS dependencies,
                collect(DISTINCT f) AS findings
            """,
            analysis_id=analysis_id
        )

        record = result.single()

        if not record:
            return None

        return {
            "analysis": dict(
                record["a"]
            ) if record["a"] else None,

            "dependencies": [
                dict(node)
                for node in record["dependencies"]
                if node
            ],

            "findings": [
                dict(node)
                for node in record["findings"]
                if node
            ],
        }

    finally:

        session.close()