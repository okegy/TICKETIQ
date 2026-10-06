package com.ticketiq.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ticketiq.dto.DashboardMetricsDto;
import com.ticketiq.dto.FeedbackRequestDto;
import com.ticketiq.dto.TicketAnalysisRequestDto;
import com.ticketiq.dto.TicketAnalysisResponseDto;
import com.ticketiq.entity.AuditEvent;
import com.ticketiq.entity.Ticket;
import com.ticketiq.entity.TicketFeedback;
import com.ticketiq.integration.ai.AiServiceClient;
import com.ticketiq.mapper.TicketMapper;
import com.ticketiq.repository.AuditEventRepository;
import com.ticketiq.repository.TicketFeedbackRepository;
import com.ticketiq.repository.TicketRepository;
import com.ticketiq.repository.mongo.TicketAiAnalysisRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class TicketServiceUnitTest {

    @Mock
    private TicketRepository ticketRepository;

    @Mock
    private TicketAiAnalysisRepository mongoAnalysisRepository;

    @Mock
    private AuditEventRepository auditEventRepository;

    @Mock
    private TicketFeedbackRepository feedbackRepository;

    @Mock
    private AiServiceClient aiServiceClient;

    @Mock
    private TicketMapper ticketMapper;

    private TicketService ticketService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        ticketService = new TicketService(
                ticketRepository,
                mongoAnalysisRepository,
                auditEventRepository,
                feedbackRepository,
                aiServiceClient,
                objectMapper,
                ticketMapper
        );
    }

    @Test
    void testCreateTicket() {
        Ticket ticket = new Ticket();
        ticket.setTitle("VPN issue");
        ticket.setRawDescription("GlobalProtect fails");

        when(ticketRepository.save(any(Ticket.class))).thenAnswer(invocation -> {
            Ticket t = invocation.getArgument(0);
            t.setId("test-uuid-1");
            return t;
        });

        Ticket created = ticketService.createTicket(ticket);
        assertNotNull(created);
        assertNotNull(created.getTicketNumber());
        assertTrue(created.getTicketNumber().startsWith("INC-"));
        verify(auditEventRepository, times(1)).save(any(AuditEvent.class));
    }

    @Test
    void testApproveTicket() {
        Ticket ticket = new Ticket();
        ticket.setId("ticket-123");
        ticket.setStatus("ANALYZED");

        when(ticketRepository.findById("ticket-123")).thenReturn(Optional.of(ticket));
        when(ticketRepository.save(any(Ticket.class))).thenReturn(ticket);

        Ticket approved = ticketService.approveTicket("ticket-123", "LeadAnalyst");
        assertEquals("APPROVED", approved.getStatus());
        verify(auditEventRepository, times(1)).save(any(AuditEvent.class));
    }

    @Test
    void testRejectTicket() {
        Ticket ticket = new Ticket();
        ticket.setId("ticket-456");
        ticket.setStatus("ANALYZED");

        when(ticketRepository.findById("ticket-456")).thenReturn(Optional.of(ticket));
        when(ticketRepository.save(any(Ticket.class))).thenReturn(ticket);

        Ticket rejected = ticketService.rejectTicket("ticket-456", "LeadAnalyst", "Bad steps");
        assertEquals("REJECTED", rejected.getStatus());
        verify(auditEventRepository, times(1)).save(any(AuditEvent.class));
    }

    @Test
    void testSubmitFeedback() {
        FeedbackRequestDto dto = new FeedbackRequestDto();
        dto.setHelpful(true);
        dto.setFeedbackNotes("Accurate steps");
        dto.setSubmittedBy("AnalystBob");

        when(feedbackRepository.save(any(TicketFeedback.class))).thenAnswer(i -> i.getArgument(0));

        TicketFeedback feedback = ticketService.submitFeedback("ticket-789", dto);
        assertNotNull(feedback);
        assertTrue(feedback.isHelpful());
        assertEquals("AnalystBob", feedback.getSubmittedBy());
        verify(auditEventRepository, times(1)).save(any(AuditEvent.class));
    }

    @Test
    void testAnalyzeTicketOrchestration() {
        Ticket ticket = new Ticket();
        ticket.setId("ticket-999");
        ticket.setTicketNumber("INC-999");
        ticket.setRawDescription("Payroll reset AUTH-401 error");

        when(ticketRepository.findById("ticket-999")).thenReturn(Optional.of(ticket));
        when(ticketRepository.save(any(Ticket.class))).thenReturn(ticket);

        TicketAnalysisResponseDto aiResponse = new TicketAnalysisResponseDto();
        aiResponse.setDecision("DRAFT_ALLOWED");
        aiResponse.setRedactedText("Payroll reset [REDACTED_ERROR]");

        when(aiServiceClient.analyzeTicket(any(TicketAnalysisRequestDto.class))).thenReturn(aiResponse);

        TicketAnalysisResponseDto result = ticketService.analyzeTicket("ticket-999", 0.50);
        assertNotNull(result);
        assertEquals("DRAFT_ALLOWED", result.getDecision());
        assertEquals("ANALYZED", ticket.getStatus());
        verify(ticketRepository, times(2)).save(ticket);
    }

    @Test
    void testDashboardMetrics() {
        Ticket t1 = new Ticket();
        t1.setStatus("APPROVED");
        Ticket t2 = new Ticket();
        t2.setStatus("REJECTED");
        Ticket t3 = new Ticket();
        t3.setStatus("NO_RELIABLE_MATCH");

        when(ticketRepository.findAll()).thenReturn(List.of(t1, t2, t3));

        DashboardMetricsDto metrics = ticketService.getDashboardMetrics();
        assertEquals(3, metrics.getTotalTickets());
        assertEquals(1, metrics.getApprovedTickets());
        assertEquals(1, metrics.getRejectedTickets());
        assertEquals(1, metrics.getNoMatchTickets());
        // positiveDecisions = approved(1) + analyzed(0); grounding = 1 / (1 + noMatch 1) = 50%
        assertEquals(50.0, metrics.getGroundingCoverageRate());
        assertEquals(90.0, metrics.getDecisionAccuracyRate());
    }
}
