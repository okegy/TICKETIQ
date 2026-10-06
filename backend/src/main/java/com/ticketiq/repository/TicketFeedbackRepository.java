package com.ticketiq.repository;

import com.ticketiq.entity.TicketFeedback;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TicketFeedbackRepository extends JpaRepository<TicketFeedback, String> {
    List<TicketFeedback> findByTicketId(String ticketId);
}
