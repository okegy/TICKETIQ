package com.ticketiq.dto;

import lombok.Data;

/**
 * Lightweight read-only view of a Ticket for list/table endpoints.
 * Contains only the fields needed by the Operations Dashboard — avoids
 * sending large TEXT columns (rawDescription, redactedDescription) over
 * the wire when they are not needed.
 */
@Data
public class TicketSummaryDto {
    private String id;
    private String ticketNumber;
    private String title;
    private String status;
    private String decisionStatus;
    private String applicationName;
    private String createdAt;
}
