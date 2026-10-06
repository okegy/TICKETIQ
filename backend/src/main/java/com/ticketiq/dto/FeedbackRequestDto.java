package com.ticketiq.dto;

import lombok.Data;

@Data
public class FeedbackRequestDto {
    private boolean helpful;
    private String feedbackNotes;
    private String categoryOverride;
    private String submittedBy;
}
