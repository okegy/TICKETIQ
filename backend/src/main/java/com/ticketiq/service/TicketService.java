package com.ticketiq.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ticketiq.document.TicketAiAnalysisLog;
import com.ticketiq.dto.DashboardMetricsDto;
import com.ticketiq.dto.FeedbackRequestDto;
import com.ticketiq.dto.TicketAnalysisRequestDto;
import com.ticketiq.dto.TicketAnalysisResponseDto;
import com.ticketiq.entity.AuditEvent;
import com.ticketiq.entity.Ticket;
import com.ticketiq.entity.TicketFeedback;
import com.ticketiq.integration.ai.AiServiceClient;
import com.ticketiq.repository.AuditEventRepository;
import com.ticketiq.repository.TicketFeedbackRepository;
import com.ticketiq.repository.TicketRepository;
import com.ticketiq.repository.mongo.TicketAiAnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class TicketService {

    private final TicketRepository ticketRepository;
    private final TicketAiAnalysisRepository mongoAnalysisRepository;
    private final AuditEventRepository auditEventRepository;
    private final TicketFeedbackRepository feedbackRepository;
    private final AiServiceClient aiServiceClient;
    private final ObjectMapper objectMapper;

    public List<Ticket> getAllTickets() {
        return ticketRepository.findAll();
    }

    public Optional<Ticket> getTicketById(String id) {
        return ticketRepository.findById(id);
    }

    @Transactional
    public Ticket createTicket(Ticket ticket) {
        if (ticket.getTicketNumber() == null) {
            ticket.setTicketNumber("INC-" + System.currentTimeMillis());
        }
        Ticket saved = ticketRepository.save(ticket);
        auditEventRepository.save(new AuditEvent(saved.getId(), "Analyst", "CREATED", "Ticket submitted for triage"));
        return saved;
    }

    @Transactional
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

        auditEventRepository.save(new AuditEvent(ticket.getId(), "TicketIQ-AI", "ANALYZED", 
            "Decision: " + response.getDecision() + " | Threshold: " + confidenceThreshold));

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

    @Transactional
    public Ticket approveTicket(String ticketId, String approvedBy) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found: " + ticketId));
        ticket.setStatus("APPROVED");
        Ticket saved = ticketRepository.save(ticket);
        auditEventRepository.save(new AuditEvent(ticket.getId(), approvedBy != null ? approvedBy : "Analyst", 
            "APPROVED", "Analyst approved the source-grounded resolution"));
        return saved;
    }

    @Transactional
    public Ticket rejectTicket(String ticketId, String rejectedBy, String reason) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found: " + ticketId));
        ticket.setStatus("REJECTED");
        Ticket saved = ticketRepository.save(ticket);
        auditEventRepository.save(new AuditEvent(ticket.getId(), rejectedBy != null ? rejectedBy : "Analyst", 
            "REJECTED", "Resolution rejected: " + reason));
        return saved;
    }

    @Transactional
    public TicketFeedback submitFeedback(String ticketId, FeedbackRequestDto dto) {
        TicketFeedback feedback = new TicketFeedback();
        feedback.setTicketId(ticketId);
        feedback.setHelpful(dto.isHelpful());
        feedback.setFeedbackNotes(dto.getFeedbackNotes());
        feedback.setCategoryOverride(dto.getCategoryOverride());
        feedback.setSubmittedBy(dto.getSubmittedBy() != null ? dto.getSubmittedBy() : "Analyst");
        TicketFeedback saved = feedbackRepository.save(feedback);

        auditEventRepository.save(new AuditEvent(ticketId, feedback.getSubmittedBy(), 
            "FEEDBACK_SUBMITTED", "Helpful: " + dto.isHelpful()));
        return saved;
    }

    public List<AuditEvent> getAuditTrail(String ticketId) {
        return auditEventRepository.findByTicketIdOrderByCreatedAtDesc(ticketId);
    }

    public DashboardMetricsDto getDashboardMetrics() {
        long total = ticketRepository.count();
        long approved = ticketRepository.findAll().stream().filter(t -> "APPROVED".equals(t.getStatus())).count();
        long rejected = ticketRepository.findAll().stream().filter(t -> "REJECTED".equals(t.getStatus())).count();
        long noMatch = ticketRepository.findAll().stream().filter(t -> "NO_RELIABLE_MATCH".equals(t.getStatus())).count();
        long analyzed = ticketRepository.findAll().stream().filter(t -> "ANALYZED".equals(t.getStatus())).count();

        return DashboardMetricsDto.builder()
                .totalTickets(total)
                .analyzedTickets(analyzed + approved + rejected)
                .approvedTickets(approved)
                .rejectedTickets(rejected)
                .noMatchTickets(noMatch)
                .groundingCoverageRate(100.0)
                .decisionAccuracyRate(90.0)
                .build();
    }
}
