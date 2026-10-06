# 🏗️ TicketIQ — Architecture & Design

## System Overview

TicketIQ is an evidence-gated, analyst-controlled retrieval copilot for IT AMS ticket classification and resolution.

```mermaid
graph TD
    A[IT Support Analyst] -->|Pastes Ticket| B[Angular Copilot UI]
    B -->|REST API| C[Spring Boot 3.3 Backend]
    C -->|Stores Ticket| D[(MySQL - System of Record)]
    C -->|Stores Audit & Telemetry| E[(MongoDB - Knowledge & Logs)]
    C -->|Delegates Analysis| F[FastAPI AI Service]
    
    subgraph AI Pipeline
        F --> G[PII Redaction Service]
        G --> H[TF-IDF Knowledge Retriever]
        H --> I[Confidence & Refusal Gate]
        I -->|Score < Threshold| J[NO_RELIABLE_MATCH]
        I -->|Score >= Threshold| K[Source-Grounded Resolution Generator]
        K --> L[Step-by-Step Verifier]
    end
    
    F -->|Returns Grounded Draft| C
    C -->|Presents to Analyst| B
    B -->|Approve / Edit / Feedback| A
```

## Key Architectural Principles

1. **Evidence Gating & Grounding**: No resolution step is presented to the analyst without an exact citation (`sourceArticleId`, `sourceSection`, `sourceStepId`).
2. **Deterministic Refusal**: If a query does not match approved knowledge articles with high confidence, the system refuses to answer (`NO_RELIABLE_MATCH`), eliminating hallucinations.
3. **Dual Storage**:
   - **MySQL**: Relational storage for transactional tickets, status transitions, and audit records.
   - **MongoDB**: Schema-free storage for deep AI telemetry, prompts, embeddings, and confidence scores.
4. **Human-in-the-Loop**: The analyst retains full control to edit, approve, reject, or provide feedback on generated resolution steps.
