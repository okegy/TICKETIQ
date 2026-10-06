package com.ticketiq.controller;

import com.ticketiq.dto.DashboardMetricsDto;
import com.ticketiq.dto.FeedbackRequestDto;
import com.ticketiq.dto.TicketAnalysisResponseDto;
import com.ticketiq.dto.TicketSummaryDto;
import com.ticketiq.entity.AuditEvent;
import com.ticketiq.entity.Ticket;
import com.ticketiq.entity.TicketFeedback;
import com.ticketiq.rules.PriorityRulesEngine;
import com.ticketiq.service.TicketService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST controller exposing the TicketIQ API under /api.
 *
 * Endpoints:
 *   GET    /api/tickets                        – list all tickets (summary view)
 *   GET    /api/tickets/{id}                   – get ticket by ID
 *   POST   /api/tickets                        – create ticket
 *   POST   /api/tickets/{id}/analyze           – trigger AI analysis
 *   POST   /api/tickets/{id}/approve           – analyst approves resolution
 *   POST   /api/tickets/{id}/reject            – analyst rejects resolution
 *   POST   /api/tickets/{id}/feedback          – submit feedback
 *   GET    /api/tickets/{id}/audit             – get audit trail
 *   POST   /api/tickets/priority               – evaluate priority rules (stateless)
 *   GET    /api/dashboard/metrics              – operations dashboard metrics
 */
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class TicketController {

    private final TicketService ticketService;
    private final PriorityRulesEngine priorityRulesEngine;

    // ── Read ─────────────────────────────────────────────────────────────────

    @GetMapping("/tickets")
    public ResponseEntity<List<TicketSummaryDto>> getAllTickets() {
        return ResponseEntity.ok(ticketService.getAllTicketSummaries());
    }

    @GetMapping("/tickets/{id}")
    public ResponseEntity<Ticket> getTicketById(@PathVariable String id) {
        return ticketService.getTicketById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // ── Write ─────────────────────────────────────────────────────────────────

    @PostMapping("/tickets")
    public ResponseEntity<Ticket> createTicket(@RequestBody Ticket ticket) {
        return ResponseEntity.ok(ticketService.createTicket(ticket));
    }

    @PostMapping("/tickets/{id}/analyze")
    public ResponseEntity<TicketAnalysisResponseDto> analyzeTicket(
            @PathVariable String id,
            @RequestParam(defaultValue = "0.15") double confidenceThreshold) {
        return ResponseEntity.ok(ticketService.analyzeTicket(id, confidenceThreshold));
    }

    @PostMapping("/tickets/{id}/approve")
    public ResponseEntity<Ticket> approveTicket(
            @PathVariable String id,
            @RequestBody(required = false) Map<String, String> body) {
        String actor = body != null ? body.get("approvedBy") : "Analyst";
        return ResponseEntity.ok(ticketService.approveTicket(id, actor));
    }

    @PostMapping("/tickets/{id}/reject")
    public ResponseEntity<Ticket> rejectTicket(
            @PathVariable String id,
            @RequestBody(required = false) Map<String, String> body) {
        String actor  = body != null ? body.get("rejectedBy") : "Analyst";
        String reason = body != null ? body.get("reason")     : "Unsatisfactory resolution draft";
        return ResponseEntity.ok(ticketService.rejectTicket(id, actor, reason));
    }

    @PostMapping("/tickets/{id}/feedback")
    public ResponseEntity<TicketFeedback> submitFeedback(
            @PathVariable String id,
            @RequestBody FeedbackRequestDto dto) {
        return ResponseEntity.ok(ticketService.submitFeedback(id, dto));
    }

    // ── Audit ─────────────────────────────────────────────────────────────────

    @GetMapping("/tickets/{id}/audit")
    public ResponseEntity<List<AuditEvent>> getAuditTrail(@PathVariable String id) {
        return ResponseEntity.ok(ticketService.getAuditTrail(id));
    }

    // ── Priority rules (stateless — no DB required) ───────────────────────────

    /**
     * Evaluate deterministic priority rules for a ticket description.
     * Request body: { "ticketText": "...", "category": "...", "subcategory": "..." }
     * This is called by the frontend immediately after analysis for the priority badge.
     */
    @PostMapping("/tickets/priority")
    public ResponseEntity<Map<String, Object>> evaluatePriority(
            @RequestBody Map<String, String> body) {
        String text = body.getOrDefault("ticketText", "");
        String cat  = body.getOrDefault("category", "");
        String sub  = body.getOrDefault("subcategory", "");
        return ResponseEntity.ok(priorityRulesEngine.evaluateAsMap(text, cat, sub));
    }

    // ── Dashboard ─────────────────────────────────────────────────────────────

    @GetMapping("/dashboard/metrics")
    public ResponseEntity<DashboardMetricsDto> getDashboardMetrics() {
        return ResponseEntity.ok(ticketService.getDashboardMetrics());
    }
}
