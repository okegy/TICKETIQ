package com.ticketiq.controller;

import com.ticketiq.dto.TicketAnalysisResponseDto;
import com.ticketiq.entity.Ticket;
import com.ticketiq.service.TicketService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tickets")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class TicketController {

    private final TicketService ticketService;

    @GetMapping
    public ResponseEntity<List<Ticket>> getAllTickets() {
        return ResponseEntity.ok(ticketService.getAllTickets());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Ticket> getTicketById(@PathVariable String id) {
        return ticketService.getTicketById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Ticket> createTicket(@RequestBody Ticket ticket) {
        return ResponseEntity.ok(ticketService.createTicket(ticket));
    }

    @PostMapping("/{id}/analyze")
    public ResponseEntity<TicketAnalysisResponseDto> analyzeTicket(
            @PathVariable String id,
            @RequestParam(defaultValue = "0.50") double confidenceThreshold) {
        return ResponseEntity.ok(ticketService.analyzeTicket(id, confidenceThreshold));
    }
}
