package com.ticketiq.integration.ai;

import com.ticketiq.dto.TicketAnalysisRequestDto;
import com.ticketiq.dto.TicketAnalysisResponseDto;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class AiServiceClient {

    private final RestTemplate restTemplate;
    private final String aiServiceUrl;

    public AiServiceClient(@Value("${ticketiq.ai-service.url:http://localhost:8000}") String aiServiceUrl) {
        this.restTemplate = new RestTemplate();
        this.aiServiceUrl = aiServiceUrl;
    }

    public TicketAnalysisResponseDto analyzeTicket(TicketAnalysisRequestDto request) {
        String endpoint = aiServiceUrl + "/ai/analyze-ticket";
        return restTemplate.postForObject(endpoint, request, TicketAnalysisResponseDto.class);
    }
}
