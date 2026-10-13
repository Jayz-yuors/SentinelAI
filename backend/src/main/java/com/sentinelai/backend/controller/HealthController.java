package com.sentinelai.backend.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HealthController {

    @GetMapping("/")
    public Map<String, Object> home() {

        Map<String, Object> response = new HashMap<>();

        response.put("status", "UP");
        response.put("service", "SentinelAI Backend");
        response.put("message", "Backend is running successfully");

        return response;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {

        Map<String, Object> response = new HashMap<>();

        response.put("status", "UP");
        response.put("service", "sentinelai-backend");

        return response;
    }
}