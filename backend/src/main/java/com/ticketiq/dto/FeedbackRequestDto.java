package com.ticketiq.dto;

import lombok.Data;

/**
 * Request DTO for analyst feedback on a resolved ticket.
 * Captured via POST /api/tickets/{id}/feedback.
 */
@Data
public class FeedbackRequestDto {
    /** True if the analyst found the resolution helpful. */
    private boolean helpful;
    /** Optional free-text notes from the analyst. */
    private String feedbackNotes;
    /** Optional category correction if the classification was wrong. */
    private String categoryOverride;
    /** Analyst ID / name — defaults to "Analyst" if omitted. */
    private String submittedBy;
}
