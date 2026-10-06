package com.ticketiq.mapper;

import com.ticketiq.dto.TicketSummaryDto;
import com.ticketiq.entity.Ticket;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Manual mapper between the Ticket JPA entity and lightweight DTOs
 * used for list views (e.g., the Operations Dashboard ticket table).
 * Using a hand-written mapper avoids the MapStruct annotation-processor
 * dependency while keeping the controller and service layers thin.
 */
@Component
public class TicketMapper {

    public TicketSummaryDto toSummary(Ticket ticket) {
        if (ticket == null) return null;
        TicketSummaryDto dto = new TicketSummaryDto();
        dto.setId(ticket.getId());
        dto.setTicketNumber(ticket.getTicketNumber());
        dto.setTitle(ticket.getTitle());
        dto.setStatus(ticket.getStatus());
        dto.setDecisionStatus(ticket.getDecisionStatus());
        dto.setApplicationName(ticket.getApplicationName());
        dto.setCreatedAt(ticket.getCreatedAt() != null ? ticket.getCreatedAt().toString() : null);
        return dto;
    }

    public List<TicketSummaryDto> toSummaryList(List<Ticket> tickets) {
        return tickets.stream().map(this::toSummary).collect(Collectors.toList());
    }
}
