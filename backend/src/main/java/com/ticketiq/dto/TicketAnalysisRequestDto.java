package com.ticketiq.dto;

import lombok.Data;
import java.util.Map;

@Data
public class TicketAnalysisRequestDto {
    private String ticketId;
    private String ticketText;
    private Map<String, Object> structuredFields;
    private int topK = 3;
    private double confidenceThreshold = 0.50;
    private String retrievalMode = "hybrid";
}
