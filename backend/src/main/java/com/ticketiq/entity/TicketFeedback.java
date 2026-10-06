package com.ticketiq.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "ticket_feedback")
@Data
@NoArgsConstructor
public class TicketFeedback {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String ticketId;

    private boolean helpful;

    @Column(columnDefinition = "TEXT")
    private String feedbackNotes;

    private String categoryOverride;
    private String submittedBy;
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}
