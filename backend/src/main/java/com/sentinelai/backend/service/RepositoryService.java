package com.sentinelai.backend.service;

import com.sentinelai.backend.dto.RepositoryRequest;
import com.sentinelai.backend.dto.RepositoryResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class RepositoryService {

    private final RestClient restClient;

    public RepositoryService(
            RestClient.Builder restClientBuilder,
            @Value("${sentinelai.ai.base-url}") String aiBaseUrl
    ) {
        this.restClient = restClientBuilder
                .baseUrl(aiBaseUrl)
                .build();
    }

    public RepositoryResponse analyzeRepository(RepositoryRequest request) {

        if (request.repositoryUrl() == null ||
                request.repositoryUrl().isBlank()) {

            throw new IllegalArgumentException(
                    "Repository URL cannot be empty"
            );
        }

        String branch = request.branch();

        if (branch == null || branch.isBlank()) {
            branch = "main";
        }

        RepositoryRequest normalizedRequest =
                new RepositoryRequest(
                        request.repositoryUrl(),
                        branch
                );

        return restClient.post()
                .uri("/analyze")
                .contentType(MediaType.APPLICATION_JSON)
                .body(normalizedRequest)
                .retrieve()
                .body(RepositoryResponse.class);
    }
}