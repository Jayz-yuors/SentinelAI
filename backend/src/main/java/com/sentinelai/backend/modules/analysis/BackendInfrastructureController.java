package com.sentinelai.backend.modules.analysis;

import com.sentinelai.backend.modules.ai.service.AnalysisService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/infrastructure")
public class BackendInfrastructureController {

    private final AnalysisService analysisService;

    private final BackendAnalysisPersistenceService
            postgresService;

    private final Neo4jBackendService
            neo4jService;

    public BackendInfrastructureController(
            AnalysisService analysisService,
            BackendAnalysisPersistenceService postgresService,
            Neo4jBackendService neo4jService
    ) {

        this.analysisService =
                analysisService;

        this.postgresService =
                postgresService;

        this.neo4jService =
                neo4jService;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>>
    infrastructureHealth() {

        boolean ai =
                analysisService.isAiServiceAvailable();

        boolean postgres =
                postgresService.databaseAvailable();

        boolean neo4j =
                neo4jService.isAvailable();

        Map<String, Object> services =
                new LinkedHashMap<>();

        services.put(
                "aiService",
                ai ? "UP" : "DOWN"
        );

        services.put(
                "postgresql",
                postgres ? "UP" : "DOWN"
        );

        services.put(
                "neo4j",
                neo4j ? "UP" : "DOWN"
        );

        boolean allHealthy =
                ai && postgres && neo4j;

        Map<String, Object> response =
                new LinkedHashMap<>();

        response.put(
                "service",
                "SentinelAI Backend"
        );

        response.put(
                "status",
                allHealthy
                        ? "UP"
                        : "DEGRADED"
        );

        response.put(
                "services",
                services
        );

        return allHealthy
                ? ResponseEntity.ok(response)
                : ResponseEntity
                    .status(503)
                    .body(response);
    }

    @GetMapping(
            "/analysis/{analysisId}"
    )
    public ResponseEntity<Map<String, Object>>
    analysisInfrastructureState(
            @PathVariable String analysisId
    ) {

        Map<String, Object> response =
                new LinkedHashMap<>();

        response.put(
                "analysisId",
                analysisId
        );

        response.put(
                "postgresql",
                postgresService
                        .getAnalysisStatus(
                                analysisId
                        )
        );

        response.put(
                "neo4j",
                neo4jService.getAnalysis(
                        analysisId
                )
        );

        return ResponseEntity.ok(response);
    }
}