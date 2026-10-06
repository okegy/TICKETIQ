package com.ticketiq.dto;

import lombok.Data;
import java.util.List;
import java.util.Map;

@Data
public class TicketAnalysisResponseDto {
    private String decision;
    private String redactedText;
    private Map<String, Object> extractedFields;
    private List<String> missingFields;
    private Map<String, Object> classification;
    private List<Map<String, Object>> evidence;
    private Map<String, Object> confidence;
    private List<Map<String, Object>> resolutionSteps;
    private Map<String, Object> escalation;
    private List<String> possibleDuplicates;
    private Map<String, Object> configuration;
}
