package com.sentinelai.backend.dto;

public record RepositoryRequest(
        String repositoryUrl,
        String branch
) {
}