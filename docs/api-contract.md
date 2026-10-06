# 📡 TicketIQ — API Contract

## 1. Spring Boot Backend Endpoints (Port 8080)

### `GET /api/tickets`
- Returns all tickets in the system.

### `POST /api/tickets`
- **Request Body:**
  ```json
  {
    "title": "VPN gateway issue",
    "rawDescription": "Cannot connect to VPN with ERR_GATEWAY_UNREACHABLE",
    "applicationName": "GlobalProtect"
  }
  ```
- **Response:** Created Ticket object with generated `ticketNumber` (e.g. `INC-1002`).

### `POST /api/tickets/{id}/analyze`
- Triggers AI pipeline analysis and updates ticket state.
- **Query Params:** `confidenceThreshold` (default: `0.50`)
- **Response:**
  ```json
  {
    "decision": "DRAFT_ALLOWED",
    "redactedText": "Cannot connect to VPN with ERR_GATEWAY_UNREACHABLE",
    "classification": {
      "category": "Network & Access",
      "subcategory": "VPN",
      "confidence": 0.78
    },
    "evidence": [...],
    "resolutionSteps": [
      {
        "stepNumber": 1,
        "instruction": "Open GlobalProtect settings and select Refresh Connection.",
        "sourceArticleId": "KB-01",
        "sourceSection": "Resolution Steps",
        "sourceStepId": "KB-01-S1",
        "verificationStatus": "SUPPORTED"
      }
    ]
  }
  ```

---

## 2. Python AI Service Endpoints (Port 8000)

### `GET /health`
- Health check endpoint. Returns `{"status": "ok", "service": "TicketIQ AI"}`.

### `POST /ai/analyze-ticket`
- Full pipeline: PII Redaction -> TF-IDF Retrieval -> Confidence Gating -> Resolution Extraction.

### `POST /ai/find-duplicates`
- Compares input ticket against historical tickets using cosine similarity.

### `POST /ai/detect-knowledge-gaps`
- Clusters repeated unmatched queries to suggest new knowledge article topics.
