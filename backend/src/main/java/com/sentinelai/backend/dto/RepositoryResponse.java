package com.sentinelai.backend.dto;

import java.util.List;

public record RepositoryResponse(
        boolean success,
        String repositoryUrl,
        String repositoryName,
        String branch,
        int totalFiles,
        List<String> languages,
        List<String> changedFiles,
        String message
) {
}