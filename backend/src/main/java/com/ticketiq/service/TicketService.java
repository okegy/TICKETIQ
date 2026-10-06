package com.ticketiq.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ticketiq.document.TicketAiAnalysisLog;
import com.ticketiq.dto.TicketAnalysisRequestDto;
import com.ticketiq.dto.TicketAnalysisResponseDto;
import com.ticketiq.entity.Ticket;
import com.ticketiq.integration.ai.AiServiceClient;
import com.ticketiq.repository.TicketRepository;
import com.ticketiq.repository.mongo.TicketAiAnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class TicketService {

    private final TicketRepository ticketRepository;
    private final TicketAiAnalysisRepository mongoAnalysisRepository;
    private final AiServiceClient aiServiceClient;
    private final ObjectMapper objectMapper;

    public List<Ticket> getAllTickets() {
        return ticketRepository.findAll();
    }

    public Optional<Ticket> getTicketById(String id) {
        return ticketRepository.findById(id);
    }

    public Ticket createTicket(Ticket ticket) {
        if (ticket.getTicketNumber() == null) {
            ticket.setTicketNumber("INC-" + System.currentTimeMillis());
        }
        return ticketRepository.save(ticket);
    }

    public TicketAnalysisResponseDto analyzeTicket(String ticketId, double confidenceThreshold) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found: " + ticketId));

        ticket.setStatus("ANALYZING");
        ticketRepository.save(ticket);

        TicketAnalysisRequestDto request = new TicketAnalysisRequestDto();
        request.setTicketId(ticket.getTicketNumber());
        request.setTicketText(ticket.getRawDescription());
        Map<String, Object> fields = new HashMap<>();
        if (ticket.getApplicationName() != null) {
            fields.put("application", ticket.getApplicationName());
        }
        request.setStructuredFields(fields);
        request.setConfidenceThreshold(confidenceThreshold);

        TicketAnalysisResponseDto response = aiServiceClient.analyzeTicket(request);

        // Update MySQL Ticket record
        ticket.setRedactedDescription(response.getRedactedText());
        ticket.setDecisionStatus(response.getDecision());
        ticket.setStatus("DRAFT_ALLOWED".equals(response.getDecision()) ? "ANALYZED" : "NO_RELIABLE_MATCH");
        ticketRepository.save(ticket);

        // Save AI Analysis Log into MongoDB
        try {
            TicketAiAnalysisLog mongoLog = new TicketAiAnalysisLog();
            mongoLog.setTicketId(ticket.getId());
            mongoLog.setDecision(response.getDecision());
            mongoLog.setRedactedText(response.getRedactedText());
            mongoLog.setFullAnalysisJson(objectMapper.convertValue(response, Map.class));
            mongoAnalysisRepository.save(mongoLog);
        } catch (Exception e) {
            System.err.println("Warning: Could not save log to MongoDB: " + e.getMessage());
        }

        return response;
    }
}
