package com.sentinelai.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sentinelai.backend.dto.RepositoryRequest;
import com.sentinelai.backend.dto.RepositoryResponse;
import com.sentinelai.backend.service.RepositoryService;

@RestController
@RequestMapping("/api/v1/repository")
public class RepositoryController {

    private final RepositoryService repositoryService;

    public RepositoryController(RepositoryService repositoryService) {
        this.repositoryService = repositoryService;
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Repository service is running");
    }

    @PostMapping("/analyze")
    public ResponseEntity<RepositoryResponse> analyze(
            @RequestBody RepositoryRequest request
    ) {

        RepositoryResponse response =
                repositoryService.analyzeRepository(request);

        return ResponseEntity.ok(response);
    }
}