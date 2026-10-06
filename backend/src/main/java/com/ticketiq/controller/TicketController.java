package com.ticketiq.controller;

import com.ticketiq.dto.DashboardMetricsDto;
import com.ticketiq.dto.FeedbackRequestDto;
import com.ticketiq.dto.TicketAnalysisResponseDto;
import com.ticketiq.entity.AuditEvent;
import com.ticketiq.entity.Ticket;
import com.ticketiq.entity.TicketFeedback;
import com.ticketiq.service.TicketService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class TicketController {

    private final TicketService ticketService;

    @GetMapping("/tickets")
    public ResponseEntity<List<Ticket>> getAllTickets() {
        return ResponseEntity.ok(ticketService.getAllTickets());
    }

    @GetMapping("/tickets/{id}")
    public ResponseEntity<Ticket> getTicketById(@PathVariable String id) {
        return ticketService.getTicketById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping("/tickets")
    public ResponseEntity<Ticket> createTicket(@RequestBody Ticket ticket) {
        return ResponseEntity.ok(ticketService.createTicket(ticket));
    }

    @PostMapping("/tickets/{id}/analyze")
    public ResponseEntity<TicketAnalysisResponseDto> analyzeTicket(
            @PathVariable String id,
            @RequestParam(defaultValue = "0.50") double confidenceThreshold) {
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
        String actor = body != null ? body.get("rejectedBy") : "Analyst";
        String reason = body != null ? body.get("reason") : "Unsatisfactory resolution draft";
        return ResponseEntity.ok(ticketService.rejectTicket(id, actor, reason));
    }

    @PostMapping("/tickets/{id}/feedback")
    public ResponseEntity<TicketFeedback> submitFeedback(
            @PathVariable String id,
            @RequestBody FeedbackRequestDto dto) {
        return ResponseEntity.ok(ticketService.submitFeedback(id, dto));
    }

    @GetMapping("/tickets/{id}/audit")
    public ResponseEntity<List<AuditEvent>> getAuditTrail(@PathVariable String id) {
        return ResponseEntity.ok(ticketService.getAuditTrail(id));
    }

    @GetMapping("/dashboard/metrics")
    public ResponseEntity<DashboardMetricsDto> getDashboardMetrics() {
        return ResponseEntity.ok(ticketService.getDashboardMetrics());
    }
}
