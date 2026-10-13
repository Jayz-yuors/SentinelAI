package com.sentinelai.backend.modules.ai.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.sentinelai.backend.modules.ai.client.AiServiceClient;
import com.sentinelai.backend.modules.ai.dto.AnalysisRequest;
import org.springframework.stereotype.Service;

@Service
public class AnalysisService {

    private final AiServiceClient aiServiceClient;

    public AnalysisService(
            AiServiceClient aiServiceClient
    ) {
        this.aiServiceClient = aiServiceClient;
    }

    /**
     * Forward repository analysis request to FastAPI.
     */
    public JsonNode analyzeRepository(
            AnalysisRequest request
    ) {

        return aiServiceClient.analyzeRepository(
                request
        );
    }

    /**
     * Retrieve existing analysis.
     */
    public JsonNode getAnalysis(
            String analysisId
    ) {

        return aiServiceClient.getAnalysis(
                analysisId
        );
    }

    /**
     * Check AI service availability.
     */
    public boolean isAiServiceAvailable() {

        return aiServiceClient.isAvailable();
    }
}