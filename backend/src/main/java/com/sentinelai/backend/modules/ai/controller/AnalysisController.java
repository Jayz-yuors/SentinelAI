package com.sentinelai.backend.modules.ai.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.sentinelai.backend.modules.ai.dto.AnalysisRequest;
import com.sentinelai.backend.modules.ai.service.AnalysisService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    private final AnalysisService analysisService;

    public AnalysisController(AnalysisService analysisService) {
        this.analysisService = analysisService;
    }

    @PostMapping(
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<String> analyzeRepository(
            @RequestBody AnalysisRequest request
    ) {

        JsonNode result = analysisService.analyzeRepository(request);

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(result.toString());
    }

    @GetMapping(
            value = "/{analysisId}",
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<String> getAnalysis(
            @PathVariable String analysisId
    ) {

        JsonNode result = analysisService.getAnalysis(analysisId);

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(result.toString());
    }

    @GetMapping("/service/status")
    public ResponseEntity<String> getServiceStatus() {

        boolean available = analysisService.isAiServiceAvailable();

        String response = """
                {
                    "service": "SentinelAI AI Service",
                    "status": "%s"
                }
                """.formatted(available ? "UP" : "DOWN");

        return ResponseEntity
                .status(available ? 200 : 503)
                .contentType(MediaType.APPLICATION_JSON)
                .body(response);
    }
}