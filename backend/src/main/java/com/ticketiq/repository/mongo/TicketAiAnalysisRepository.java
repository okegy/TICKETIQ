package com.ticketiq.repository.mongo;

import com.ticketiq.document.TicketAiAnalysisLog;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TicketAiAnalysisRepository extends MongoRepository<TicketAiAnalysisLog, String> {
    List<TicketAiAnalysisLog> findByTicketId(String ticketId);
}
