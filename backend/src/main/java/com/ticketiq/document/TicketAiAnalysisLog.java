package com.ticketiq.document;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.time.LocalDateTime;
import java.util.Map;

@Data
@Document(collection = "ticket_ai_analyses")
public class TicketAiAnalysisLog {

    @Id
    private String id;
    private String ticketId;
    private String decision;
    private String redactedText;
    private Map<String, Object> fullAnalysisJson;
    private LocalDateTime timestamp;

    public TicketAiAnalysisLog() {
        this.timestamp = LocalDateTime.now();
    }
}
