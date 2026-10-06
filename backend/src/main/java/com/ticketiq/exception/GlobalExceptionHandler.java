package com.ticketiq.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.client.ResourceAccessException;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Centralised exception handling for all REST controllers.
 * Returns a consistent JSON error envelope so the Angular frontend
 * can display meaningful error messages.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    // ── Not Found ────────────────────────────────────────────────────────────
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<Map<String, Object>> handleRuntime(RuntimeException ex) {
        String msg = ex.getMessage() != null ? ex.getMessage() : "Internal error";
        HttpStatus status = msg.toLowerCase().contains("not found")
                ? HttpStatus.NOT_FOUND
                : HttpStatus.INTERNAL_SERVER_ERROR;
        return buildResponse(status, msg);
    }

    // ── AI Service unreachable ────────────────────────────────────────────────
    @ExceptionHandler(ResourceAccessException.class)
    public ResponseEntity<Map<String, Object>> handleResourceAccess(ResourceAccessException ex) {
        return buildResponse(
                HttpStatus.SERVICE_UNAVAILABLE,
                "AI Service unreachable: " + ex.getMessage()
        );
    }

    // ── Illegal argument (e.g. bad threshold value) ───────────────────────────
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalArg(IllegalArgumentException ex) {
        return buildResponse(HttpStatus.BAD_REQUEST, ex.getMessage());
    }

    // ── Generic fallback ──────────────────────────────────────────────────────
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneric(Exception ex) {
        return buildResponse(HttpStatus.INTERNAL_SERVER_ERROR, ex.getMessage());
    }

    // ── Helper ────────────────────────────────────────────────────────────────
    private ResponseEntity<Map<String, Object>> buildResponse(HttpStatus status, String message) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("timestamp", LocalDateTime.now().toString());
        body.put("status", status.value());
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        return ResponseEntity.status(status).body(body);
    }
}
