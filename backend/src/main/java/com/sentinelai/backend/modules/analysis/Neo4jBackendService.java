package com.sentinelai.backend.modules.analysis;

import org.neo4j.driver.AuthTokens;
import org.neo4j.driver.Driver;
import org.neo4j.driver.GraphDatabase;
import org.neo4j.driver.SessionConfig;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class Neo4jBackendService {

    private final Driver driver;

    private final String database;

    public Neo4jBackendService(
            @Value(
                    "${sentinelai.neo4j.uri:bolt://localhost:7687}"
            )
            String uri,

            @Value(
                    "${sentinelai.neo4j.username:neo4j}"
            )
            String username,

            @Value(
                    "${sentinelai.neo4j.password}"
            )
            String password,

            @Value(
                    "${sentinelai.neo4j.database:neo4j}"
            )
            String database
    ) {

        this.database = database;

        this.driver =
                GraphDatabase.driver(
                        uri,
                        AuthTokens.basic(
                                username,
                                password
                        )
                );
    }

    /**
     * Verify Neo4j connectivity.
     */
    public boolean isAvailable() {

        try {

            driver.verifyConnectivity();

            return true;

        } catch (Exception exception) {

            return false;
        }
    }

    /**
     * Create/update a backend reference to an analysis.
     *
     * This proves that the Spring Boot backend can
     * communicate with the same Neo4j graph used by
     * SentinelAI.
     */
    public Map<String, Object> synchronizeAnalysis(
            String analysisId,
            String repositoryUrl,
            String status
    ) {

        try {

            var result =
                    driver.executableQuery(
                            """
                            MERGE (a:BackendAnalysis
                                   {analysisId: $analysisId})
                            SET
                                a.repositoryUrl = $repositoryUrl,
                                a.status = $status,
                                a.updatedAt = datetime()
                            RETURN
                                a.analysisId AS analysisId,
                                a.status AS status
                            """
                    )
                    .withParameters(
                            Map.of(
                                    "analysisId",
                                    analysisId,
                                    "repositoryUrl",
                                    repositoryUrl,
                                    "status",
                                    status
                            )
                    )
                    .withConfig(
                            org.neo4j.driver.QueryConfig
                                    .builder()
                                    .withDatabase(database)
                                    .build()
                    )
                    .execute();

            Map<String, Object> response =
                    new LinkedHashMap<>();

            response.put(
                    "success",
                    true
            );

            response.put(
                    "analysisId",
                    analysisId
            );

            response.put(
                    "status",
                    status
            );

            response.put(
                    "records",
                    result.records().size()
            );

            return response;

        } catch (Exception exception) {

            throw new RuntimeException(
                    "Neo4j synchronization failed: "
                            + exception.getMessage(),
                    exception
            );
        }
    }

    /**
     * Read backend analysis node.
     */
    public Map<String, Object> getAnalysis(
            String analysisId
    ) {

        try {

            var result =
                    driver.executableQuery(
                            """
                            MATCH (
                                a:BackendAnalysis
                                {analysisId: $analysisId}
                            )
                            RETURN
                                a.analysisId AS analysisId,
                                a.repositoryUrl AS repositoryUrl,
                                a.status AS status,
                                a.updatedAt AS updatedAt
                            """
                    )
                    .withParameters(
                            Map.of(
                                    "analysisId",
                                    analysisId
                            )
                    )
                    .withConfig(
                            org.neo4j.driver.QueryConfig
                                    .builder()
                                    .withDatabase(database)
                                    .build()
                    )
                    .execute();

            if (result.records().isEmpty()) {
                return Map.of();
            }

            var record =
                    result.records().get(0);

            Map<String, Object> response =
                    new LinkedHashMap<>();

            response.put(
                    "analysisId",
                    record.get("analysisId").asString()
            );

            response.put(
                    "repositoryUrl",
                    record.get("repositoryUrl").asString()
            );

            response.put(
                    "status",
                    record.get("status").asString()
            );

            response.put(
                    "updatedAt",
                    record.get("updatedAt").toString()
            );

            return response;

        } catch (Exception exception) {

            throw new RuntimeException(
                    "Neo4j analysis lookup failed: "
                            + exception.getMessage(),
                    exception
            );
        }
    }
}