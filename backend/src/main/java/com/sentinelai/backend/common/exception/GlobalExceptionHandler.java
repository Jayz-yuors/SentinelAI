package com.sentinelai.backend.common.exception;

import com.sentinelai.backend.modules.ai.exception.AiServiceException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(AiServiceException.class)
    public ResponseEntity<Map<String, Object>>
    handleAiServiceException(
            AiServiceException exception
    ) {

        HttpStatus status;

        if (exception.getStatusCode() >= 400
                && exception.getStatusCode() < 600) {

            try {

                status = HttpStatus.valueOf(
                        exception.getStatusCode()
                );

            } catch (IllegalArgumentException ignored) {

                status =
                        HttpStatus.BAD_GATEWAY;
            }

        } else {

            status =
                    HttpStatus.BAD_GATEWAY;
        }

        Map<String, Object> response =
                new LinkedHashMap<>();

        response.put(
                "success",
                false
        );

        response.put(
                "service",
                "SentinelAI Backend"
        );

        response.put(
                "error",
                "AI_SERVICE_ERROR"
        );

        response.put(
                "message",
                exception.getMessage()
        );

        response.put(
                "timestamp",
                Instant.now().toString()
        );

        return ResponseEntity
                .status(status)
                .body(response);
    }

    @ExceptionHandler(
            IllegalArgumentException.class
    )
    public ResponseEntity<Map<String, Object>>
    handleIllegalArgument(
            IllegalArgumentException exception
    ) {

        Map<String, Object> response =
                new LinkedHashMap<>();

        response.put(
                "success",
                false
        );

        response.put(
                "error",
                "INVALID_REQUEST"
        );

        response.put(
                "message",
                exception.getMessage()
        );

        response.put(
                "timestamp",
                Instant.now().toString()
        );

        return ResponseEntity
                .badRequest()
                .body(response);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>>
    handleGenericException(
            Exception exception
    ) {

        Map<String, Object> response =
                new LinkedHashMap<>();

        response.put(
                "success",
                false
        );

        response.put(
                "error",
                "INTERNAL_SERVER_ERROR"
        );

        response.put(
                "message",
                exception.getMessage()
        );

        response.put(
                "timestamp",
                Instant.now().toString()
        );

        return ResponseEntity
                .status(
                        HttpStatus.INTERNAL_SERVER_ERROR
                )
                .body(response);
    }
}