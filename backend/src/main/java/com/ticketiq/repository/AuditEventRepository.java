package com.ticketiq.repository;

import com.ticketiq.entity.AuditEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AuditEventRepository extends JpaRepository<AuditEvent, String> {
    List<AuditEvent> findByTicketIdOrderByCreatedAtDesc(String ticketId);
}
