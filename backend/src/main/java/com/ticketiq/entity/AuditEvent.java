package com.ticketiq.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "audit_events")
@Data
@NoArgsConstructor
public class AuditEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    private String ticketId;
    private String actor;
    private String eventType; // e.g. CREATED, ANALYZED, EDITED, APPROVED, REJECTED, FEEDBACK_SUBMITTED

    @Column(columnDefinition = "TEXT")
    private String details;

    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }

    public AuditEvent(String ticketId, String actor, String eventType, String details) {
        this.ticketId = ticketId;
        this.actor = actor;
        this.eventType = eventType;
        this.details = details;
        this.createdAt = LocalDateTime.now();
    }
}
