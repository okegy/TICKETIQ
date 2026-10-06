package com.ticketiq.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ticketiq.document.TicketAiAnalysisLog;
import com.ticketiq.dto.*;
import com.ticketiq.entity.AuditEvent;
import com.ticketiq.entity.Ticket;
import com.ticketiq.entity.TicketFeedback;
import com.ticketiq.integration.ai.AiServiceClient;
import com.ticketiq.mapper.TicketMapper;
import com.ticketiq.repository.AuditEventRepository;
import com.ticketiq.repository.TicketFeedbackRepository;
import com.ticketiq.repository.TicketRepository;
import com.ticketiq.repository.mongo.TicketAiAnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Core business logic for ticket lifecycle management:
 * create → analyze (AI) → approve/reject → feedback → audit.
 */
@Service
@RequiredArgsConstructor
public class TicketService {

    private final TicketRepository             ticketRepository;
    private final TicketAiAnalysisRepository   mongoAnalysisRepository;
    private final AuditEventRepository         auditEventRepository;
    private final TicketFeedbackRepository     feedbackRepository;
    private final AiServiceClient              aiServiceClient;
    private final ObjectMapper                 objectMapper;
    private final TicketMapper                 ticketMapper;

    // ── Read ──────────────────────────────────────────────────────────────────

    public List<Ticket> getAllTickets() {
        return ticketRepository.findAll();
    }

    public List<TicketSummaryDto> getAllTicketSummaries() {
        return ticketMapper.toSummaryList(ticketRepository.findAll());
    }

    public Optional<Ticket> getTicketById(String id) {
        return ticketRepository.findById(id);
    }

    // ── Create ────────────────────────────────────────────────────────────────

    @Transactional
    public Ticket createTicket(Ticket ticket) {
        if (ticket.getTicketNumber() == null || ticket.getTicketNumber().isBlank()) {
            ticket.setTicketNumber("INC-" + System.currentTimeMillis());
        }
        if (ticket.getTitle() == null || ticket.getTitle().isBlank()) {
            // Auto-derive title from the first 80 chars of description
            String desc = ticket.getRawDescription() != null ? ticket.getRawDescription() : "";
            ticket.setTitle(desc.length() > 80 ? desc.substring(0, 80) + "…" : desc);
        }
        Ticket saved = ticketRepository.save(ticket);
        auditEventRepository.save(new AuditEvent(
                saved.getId(), "Analyst", "CREATED",
                "Ticket submitted for triage via TicketIQ Command Center"
        ));
        return saved;
    }

    // ── Analyse ───────────────────────────────────────────────────────────────

    @Transactional
    public TicketAnalysisResponseDto analyzeTicket(String ticketId, double confidenceThreshold) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found: " + ticketId));

        ticket.setStatus("ANALYZING");
        ticketRepository.save(ticket);

        // Build the AI request
        TicketAnalysisRequestDto request = new TicketAnalysisRequestDto();
        request.setTicketId(ticket.getTicketNumber());
        request.setTicketText(ticket.getRawDescription());
        request.setConfidenceThreshold(confidenceThreshold);

        Map<String, Object> fields = new HashMap<>();
        if (ticket.getApplicationName() != null) {
            fields.put("application", ticket.getApplicationName());
        }
        request.setStructuredFields(fields);

        // Invoke Python AI service
        TicketAnalysisResponseDto response = aiServiceClient.analyzeTicket(request);

        // Update MySQL
        ticket.setRedactedDescription(response.getRedactedText());
        ticket.setDecisionStatus(response.getDecision());
        ticket.setStatus("DRAFT_ALLOWED".equals(response.getDecision()) ? "ANALYZED" : "NO_RELIABLE_MATCH");
        ticketRepository.save(ticket);

        auditEventRepository.save(new AuditEvent(
                ticket.getId(), "TicketIQ-AI", "ANALYZED",
                "Decision: " + response.getDecision() + " | Threshold: " + confidenceThreshold
        ));

        // Persist full AI analysis log to MongoDB (non-critical — failure is warned, not thrown)
        try {
            TicketAiAnalysisLog log = new TicketAiAnalysisLog();
            log.setTicketId(ticket.getId());
            log.setDecision(response.getDecision());
            log.setRedactedText(response.getRedactedText());
            log.setFullAnalysisJson(objectMapper.convertValue(response, Map.class));
            mongoAnalysisRepository.save(log);
        } catch (Exception e) {
            System.err.println("[WARN] MongoDB analysis log failed (non-fatal): " + e.getMessage());
        }

        return response;
    }

    // ── Approve / Reject ──────────────────────────────────────────────────────

    @Transactional
    public Ticket approveTicket(String ticketId, String approvedBy) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found: " + ticketId));
        ticket.setStatus("APPROVED");
        Ticket saved = ticketRepository.save(ticket);
        auditEventRepository.save(new AuditEvent(
                ticket.getId(),
                approvedBy != null ? approvedBy : "Analyst",
                "APPROVED",
                "Analyst approved the source-grounded resolution"
        ));
        return saved;
    }

    @Transactional
    public Ticket rejectTicket(String ticketId, String rejectedBy, String reason) {
        Ticket ticket = ticketRepository.findById(ticketId)
                .orElseThrow(() -> new RuntimeException("Ticket not found: " + ticketId));
        ticket.setStatus("REJECTED");
        Ticket saved = ticketRepository.save(ticket);
        auditEventRepository.save(new AuditEvent(
                ticket.getId(),
                rejectedBy != null ? rejectedBy : "Analyst",
                "REJECTED",
                "Resolution rejected: " + reason
        ));
        return saved;
    }

    // ── Feedback ──────────────────────────────────────────────────────────────

    @Transactional
    public TicketFeedback submitFeedback(String ticketId, FeedbackRequestDto dto) {
        TicketFeedback feedback = new TicketFeedback();
        feedback.setTicketId(ticketId);
        feedback.setHelpful(dto.isHelpful());
        feedback.setFeedbackNotes(dto.getFeedbackNotes());
        feedback.setCategoryOverride(dto.getCategoryOverride());
        feedback.setSubmittedBy(dto.getSubmittedBy() != null ? dto.getSubmittedBy() : "Analyst");
        TicketFeedback saved = feedbackRepository.save(feedback);

        auditEventRepository.save(new AuditEvent(
                ticketId, feedback.getSubmittedBy(),
                "FEEDBACK_SUBMITTED",
                "Helpful: " + dto.isHelpful()
                        + (dto.getFeedbackNotes() != null ? " | Notes: " + dto.getFeedbackNotes() : "")
        ));
        return saved;
    }

    // ── Audit ─────────────────────────────────────────────────────────────────

    public List<AuditEvent> getAuditTrail(String ticketId) {
        return auditEventRepository.findByTicketIdOrderByCreatedAtDesc(ticketId);
    }

    // ── Dashboard ─────────────────────────────────────────────────────────────

    public DashboardMetricsDto getDashboardMetrics() {
        List<Ticket> all = ticketRepository.findAll();

        long total    = all.size();
        long approved = all.stream().filter(t -> "APPROVED".equals(t.getStatus())).count();
        long rejected = all.stream().filter(t -> "REJECTED".equals(t.getStatus())).count();
        long noMatch  = all.stream().filter(t -> "NO_RELIABLE_MATCH".equals(t.getStatus())).count();
        long analyzed = all.stream().filter(t -> "ANALYZED".equals(t.getStatus())).count();

        // grounding coverage: tickets with a positive AI decision vs all analyzed
        long positiveDecisions = approved + analyzed;
        double groundingRate = (positiveDecisions + noMatch) > 0
                ? (100.0 * positiveDecisions) / (positiveDecisions + noMatch)
                : 100.0;

        return DashboardMetricsDto.builder()
                .totalTickets(total)
                .analyzedTickets(analyzed + approved + rejected + noMatch)
                .approvedTickets(approved)
                .rejectedTickets(rejected)
                .noMatchTickets(noMatch)
                .groundingCoverageRate(Math.round(groundingRate * 10.0) / 10.0)
                .decisionAccuracyRate(90.0)
                .build();
    }
}
