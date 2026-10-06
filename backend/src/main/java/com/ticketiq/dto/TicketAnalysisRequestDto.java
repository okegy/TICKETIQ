package com.ticketiq.dto;

import lombok.Data;

import java.util.Map;

/**
 * Request body sent from Spring Boot to the Python AI service for ticket analysis.
 */
@Data
public class TicketAnalysisRequestDto {
    private String ticketId;
    private String ticketText;
    private Map<String, Object> structuredFields;
    private double confidenceThreshold = 0.15;
    private String retrievalMode = "hybrid";
    private int topK = 3;
}
