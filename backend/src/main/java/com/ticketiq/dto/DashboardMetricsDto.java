package com.ticketiq.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class DashboardMetricsDto {
    private long totalTickets;
    private long analyzedTickets;
    private long approvedTickets;
    private long rejectedTickets;
    private long noMatchTickets;
    private double groundingCoverageRate;
    private double decisionAccuracyRate;
}
