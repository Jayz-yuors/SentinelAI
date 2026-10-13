package com.sentinelai.backend.modules.ai.dto;

public record AnalysisRequest(
        String repositoryUrl,
        String branch
) {

    public AnalysisRequest {
        if (repositoryUrl == null || repositoryUrl.isBlank()) {
            throw new IllegalArgumentException(
                    "repositoryUrl must not be empty"
            );
        }

        if (branch == null || branch.isBlank()) {
            branch = "main";
        }
    }
}