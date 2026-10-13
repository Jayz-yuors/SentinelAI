package com.sentinelai.backend.modules.ai.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.sentinelai.backend.modules.ai.dto.AnalysisRequest;
import com.sentinelai.backend.modules.ai.exception.AiServiceException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.net.ConnectException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

@Service
public class AiServiceClient {

    private final ObjectMapper objectMapper;

    private final HttpClient httpClient;

    private final String aiServiceBaseUrl;

    private final int timeoutSeconds;

    public AiServiceClient(
            ObjectMapper objectMapper,
            @Value("${sentinelai.ai.base-url:http://localhost:8000}")
            String aiServiceBaseUrl,
            @Value("${sentinelai.ai.timeout-seconds:120}")
            int timeoutSeconds
    ) {

        this.objectMapper = objectMapper;

        this.aiServiceBaseUrl =
                aiServiceBaseUrl.replaceAll("/+$", "");

        this.timeoutSeconds = timeoutSeconds;

        this.httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .connectTimeout(
                        Duration.ofSeconds(
                                Math.min(timeoutSeconds, 30)
                        )
                )
                .build();
    }


    /**
     * Execute complete AI analysis through FastAPI.
     */
    public JsonNode analyzeRepository(
            AnalysisRequest request
    ) {

        try {

            /*
             * Build the AI request explicitly.
             *
             * This intentionally avoids relying on the global
             * Jackson naming strategy configured elsewhere in
             * the Spring Boot application.
             *
             * FastAPI expects:
             *
             * {
             *     "repositoryUrl": "...",
             *     "branch": "..."
             * }
             */

            ObjectNode requestJson =
                    objectMapper.createObjectNode();

            requestJson.put(
                    "repositoryUrl",
                    request.repositoryUrl()
            );

            requestJson.put(
                    "branch",
                    request.branch()
            );

            String requestBody =
                    requestJson.toString();

            String endpoint =
                    aiServiceBaseUrl
                            + "/pipeline/analyze";

            HttpRequest httpRequest =
                    HttpRequest.newBuilder()
                            .uri(URI.create(endpoint))
                            .timeout(
                                    Duration.ofSeconds(
                                            timeoutSeconds
                                    )
                            )
                            .header(
                                    "Content-Type",
                                    "application/json"
                            )
                            .header(
                                    "Accept",
                                    "application/json"
                            )
                            .POST(
                                    HttpRequest.BodyPublishers
                                            .ofString(requestBody)
                            )
                            .build();

            HttpResponse<String> response =
                    httpClient.send(
                            httpRequest,
                            HttpResponse.BodyHandlers.ofString()
                    );

            int statusCode =
                    response.statusCode();

            String responseBody =
                    response.body();

            if (statusCode < 200 || statusCode >= 300) {

                throw new AiServiceException(
                        "AI service returned HTTP "
                                + statusCode
                                + ": "
                                + responseBody,
                        statusCode
                );
            }

            JsonNode jsonResponse =
                    objectMapper.readTree(responseBody);

            if (
                    jsonResponse.has("success")
                            &&
                            !jsonResponse
                                    .get("success")
                                    .asBoolean()
            ) {

                String message =
                        jsonResponse.has("message")
                                ? jsonResponse
                                .get("message")
                                .asText()
                                : "AI analysis failed";

                throw new AiServiceException(
                        message,
                        statusCode
                );
            }

            return jsonResponse;

        } catch (AiServiceException exception) {

            throw exception;

        } catch (java.net.http.HttpTimeoutException exception) {

            throw new AiServiceException(
                    "AI service request timed out after "
                            + timeoutSeconds
                            + " seconds",
                    exception
            );

        } catch (ConnectException exception) {

            throw new AiServiceException(
                    "Unable to connect to AI service at "
                            + aiServiceBaseUrl,
                    exception
            );

        } catch (InterruptedException exception) {

            Thread.currentThread().interrupt();

            throw new AiServiceException(
                    "AI service request was interrupted",
                    exception
            );

        } catch (IOException exception) {

            throw new AiServiceException(
                    "Failed to communicate with AI service: "
                            + exception.getMessage(),
                    exception
            );
        }
    }


    /**
     * Retrieve the status/result of a previously submitted analysis.
     */
    public JsonNode getAnalysis(
            String analysisId
    ) {

        if (analysisId == null || analysisId.isBlank()) {

            throw new IllegalArgumentException(
                    "analysisId must not be empty"
            );
        }

        try {

            String endpoint =
                    aiServiceBaseUrl
                            + "/pipeline/"
                            + analysisId;

            HttpRequest request =
                    HttpRequest.newBuilder()
                            .uri(URI.create(endpoint))
                            .timeout(
                                    Duration.ofSeconds(
                                            timeoutSeconds
                                    )
                            )
                            .header(
                                    "Accept",
                                    "application/json"
                            )
                            .GET()
                            .build();

            HttpResponse<String> response =
                    httpClient.send(
                            request,
                            HttpResponse.BodyHandlers.ofString()
                    );

            if (
                    response.statusCode() < 200
                            ||
                            response.statusCode() >= 300
            ) {

                throw new AiServiceException(
                        "AI service returned HTTP "
                                + response.statusCode()
                                + ": "
                                + response.body(),
                        response.statusCode()
                );
            }

            return objectMapper.readTree(
                    response.body()
            );

        } catch (AiServiceException exception) {

            throw exception;

        } catch (java.net.http.HttpTimeoutException exception) {

            throw new AiServiceException(
                    "AI service status request timed out",
                    exception
            );

        } catch (InterruptedException exception) {

            Thread.currentThread().interrupt();

            throw new AiServiceException(
                    "AI service status request interrupted",
                    exception
            );

        } catch (IOException exception) {

            throw new AiServiceException(
                    "Failed to retrieve analysis result: "
                            + exception.getMessage(),
                    exception
            );
        }
    }


    /**
     * Check whether the FastAPI service is reachable.
     */
    public boolean isAvailable() {

        try {

            String endpoint =
                    aiServiceBaseUrl + "/health";

            HttpRequest request =
                    HttpRequest.newBuilder()
                            .version(HttpClient.Version.HTTP_1_1)
                            .uri(URI.create(endpoint))
                            .timeout(
                                    Duration.ofSeconds(5)
                            )
                            .GET()
                            .build();

            HttpResponse<String> response =
                    httpClient.send(
                            request,
                            HttpResponse.BodyHandlers.ofString()
                    );

            return response.statusCode() >= 200
                    && response.statusCode() < 300;

        } catch (Exception exception) {

            return false;
        }
    }


    public String getAiServiceBaseUrl() {

        return aiServiceBaseUrl;
    }
}