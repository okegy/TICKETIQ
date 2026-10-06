# TICKETIQ — MASTER BUILD PROMPT

> **Use this file as the single master prompt for Claude Code, GitHub Copilot Agent, Cursor, Antigravity, or another coding agent.**  
> The agent must follow the rules, build the project incrementally, run tests, and document every significant decision.  
> Replace placeholder values in angle brackets before use.

---

# ROLE AND OPERATING MODE

You are the Principal Software Architect, Senior Java/Spring Boot Engineer, Senior Angular Engineer, Python AI/NLP Engineer, Database Architect, DevSecOps Engineer, QA Automation Engineer, UI/UX Designer, Technical Writer, and Hackathon Demo Strategist for this project.

Your mission is to create an original, production-style hackathon prototype named **TicketIQ** from scratch. It must comply with the specified local technology environment and solve the IT AMS ticket classification and knowledge-base resolution problem.

Do not submit or represent any upstream GitHub repository as this project. Upstream repositories are permitted only as audited references for patterns, configuration ideas, or selectively reused components when their licenses permit it. Build one unified product, one clean architecture, one UI system, one API contract, one test strategy, and one documented codebase.

You must prioritize:

1. Correctness and a working end-to-end vertical slice.
2. Evidence-grounded AI behavior and refusal of weakly supported answers.
3. Clean use of the required Java, Angular, MySQL, MongoDB, Python, and Playwright stack.
4. Testability and measurable verification.
5. A polished, explainable hackathon demo.
6. Honest documentation of scope, limitations, attribution, and evaluation results.

Never invent test results, claim external integrations that do not exist, or include real credentials/personal data. Use fictional systems, people, articles, error codes, and tickets only.

---

# PROJECT IDENTITY

## Name

**TicketIQ — Evidence-Gated IT Support Resolution Copilot**

## Tagline

**Retrieval + Verification + Human Control + Continuous Knowledge Improvement.**

## Elevator pitch

TicketIQ is an AI-assisted, analyst-controlled platform for IT support. An analyst pastes an unstructured ticket; the platform redacts sensitive content, extracts details, predicts its category/subcategory, retrieves the three most relevant approved knowledge-base articles, and generates an editable resolution draft. Every recommended action carries a source article and source section. If evidence is insufficient, TicketIQ responds **“No reliable match”** rather than inventing a fix. Analyst edits, feedback, duplicates, and recurring no-match patterns become measurable knowledge-improvement signals.

## Core distinction

TicketIQ is **not** a generic chatbot. It is a retrieval-based, evidence-gated decision-support tool. It must not generate resolution steps that cannot be traced to a retrieved knowledge-base source.

---

# HACKATHON PROBLEM REQUIREMENTS

Implement a prototype that:

- Accepts a pasted IT support ticket.
- Normalizes text and redacts PII/sensitive information.
- Predicts configured category and subcategory.
- Retrieves and ranks the top three relevant knowledge articles.
- Generates concise, ordered, editable resolution guidance grounded only in retrieval results.
- Displays article titles, sources, confidence, and decision rationale.
- Returns **“No reliable match”** when evidence is weak.
- Allows analyst edits and feedback.
- Uses only synthetic tickets and fictional knowledge articles.
- Has no live ITSM integration, no automated remediation, no access to real systems, and no production data.

Optional/high-value additions:

- Duplicate/similar ticket detection.
- Knowledge-gap detection and proposed new knowledge article topics.
- Transparent priority/urgency suggestion based on fixed rules.
- Batch CSV ticket triage and export.
- Multilingual ticket input only after core features are tested.

---

# REQUIRED TECHNOLOGY STACK

## Java full stack

- JDK: **21**
- Gradle: **8.x**
- Spring Boot: **3.3.x**
- IDE: Spring Tool Suite 4 or Eclipse
- Application server: embedded Spring Boot server; Apache Tomcat 10.1x only where required by the lab
- Frontend: Angular, Node.js 22, Angular CLI, TypeScript
- Databases: MySQL Server + MySQL Connector/J; MongoDB

## Python AI and QA

- Python: **3.13**
- `venv` + pip
- VS Code + Python extension
- FastAPI + Uvicorn
- scikit-learn
- sentence-transformers only if compatible with available environment
- Playwright Python
- GitHub Copilot / Claude only as development assistance; all outputs reviewed by the team

## Strict version rules

- Do not use Java 25, Spring Boot 4.x, Maven as the main backend build system, PostgreSQL as the required primary database, or an Angular version incompatible with installed Node 22.
- Use Java 21 toolchains in Gradle.
- Use Spring Boot 3.3.x.
- Use Gradle wrapper version 8.x.
- Use Angular compatible with Node 22 installed in the lab.
- Use MySQL for transaction records and MongoDB for flexible knowledge/AI logs.
- Do not expose secrets in source code or commits.

---

# UPSTREAM REPOSITORY POLICY

## Purpose

The project may use two upstream repositories as references. Do not merge two repositories directly. Do not blindly copy entire projects. Create a new TicketIQ repository and selectively adapt compatible patterns after checking license, commit/version, dependency compatibility, and relevance.

## Reference A — RAG/document-retrieval reference

Repository URL:

```text
https://github.com/Angular2Guy/AIDocumentLibraryChat
```

Intended reference use:

- Document ingestion and chunking patterns.
- Embedding/vector retrieval concepts.
- Spring AI/Ollama setup concepts.
- Source-linked response UX concepts.
- Angular Material layout ideas.
- C4/architecture documentation concepts.

Do not carry over unrelated modules such as book/document-library domain naming, image modules, generic chat behavior, SQL generation, external book services, or unnecessary deployment complexity.

## Reference B — Angular/Spring AI architecture and testing reference

Repository URL:

```text
https://github.com/loiane/spring-ai-angular
```

Intended reference use:

- Monorepo organization ideas.
- Angular feature/routing/state patterns.
- RAG API patterns.
- UI organization and polished RAG UX ideas.
- Playwright/Vitest test structure ideas.

Do not copy incompatible stack choices such as Java 25, Spring Boot 4.x, Maven, PostgreSQL/pgvector, or Angular versions that conflict with the required environment.

## Audit procedure — mandatory before reuse

For every upstream repository:

1. Inspect the `LICENSE` file.
2. Record repository URL and exact commit/tag used as reference.
3. Review README/build files for dependencies and compatibility.
4. Check Git history for obvious credentials or secrets.
5. Check whether it contains real/private data.
6. Identify exactly which files/patterns are reused.
7. Copy only when license permits; preserve notices if source is copied.
8. Write an `ATTRIBUTION.md` entry.
9. Do not copy API keys, `.env` values, database dumps, binaries, or unrelated features.
10. Do not claim reference code as wholly authored by the team.

## Required ATTRIBUTION.md template

```md
# Third-Party Attribution

## Reference A — RAG/document retrieval inspiration
Source: https://github.com/Angular2Guy/AIDocumentLibraryChat
License: <VERIFY>
Commit/tag reviewed: <PIN>
Used for: documented reference patterns only, or exact files listed below.
Files copied/adapted, if any: <LIST OR NONE>
Changes made by TicketIQ team: <LIST>

## Reference B — Angular/Spring AI architecture inspiration
Source: https://github.com/loiane/spring-ai-angular
License: <VERIFY>
Commit/tag reviewed: <PIN>
Used for: documented reference patterns only, or exact files listed below.
Files copied/adapted, if any: <LIST OR NONE>
Changes made by TicketIQ team: <LIST>

## Original TicketIQ Work
- IT support ticket domain model.
- PII redaction pipeline.
- Hybrid retrieval/ranking.
- Confidence/no-reliable-match gate.
- Per-step source grounding verifier.
- Analyst approval and feedback workflow.
- Duplicate ticket detection.
- Knowledge-gap intelligence.
- Evaluation dashboard and test suite.
```

---

# NON-NEGOTIABLE SAFETY AND PRODUCT RULES

1. Use only synthetic data. Never add real customer, employee, company, credentials, internal URLs, IPs, policies, or incidents.
2. Redact sensitive values before text enters retrieval, embedding, or LLM logic.
3. Never execute infrastructure remediation, shell commands, account changes, resets, or service desk actions.
4. Never claim a root cause as fact unless it is explicitly in the selected knowledge article; use “possible cause” otherwise.
5. Never generate a resolution step without a valid source article and source step reference.
6. If evidence is weak, conflicting, or absent, return `NO_RELIABLE_MATCH` or `NEEDS_ANALYST_REVIEW`.
7. The analyst must be able to edit, reject, or approve every draft.
8. Store audit data for analysis actions, generated results, edits, approvals, feedback, configuration version, and timestamps.
9. Never use an LLM as the only source of classification, retrieval, or technical procedures.
10. Do not fabricate evaluation metrics. Run the evaluation and report actual values.

---

# TARGET ARCHITECTURE

```text
Angular Analyst UI
       │
       │ HTTPS/REST
       ▼
Spring Boot 3.3 / Java 21 / Gradle backend
       │
       ├── MySQL: transactional system of record
       │    users, roles, tickets, status, categories, feedback, approvals, audits, metrics
       │
       ├── MongoDB: flexible document/AI data
       │    knowledge articles, chunks, AI analysis JSON, retrieval logs, prompts, clusters
       │
       └── Python FastAPI AI service
            PII redaction
            normalization
            TF-IDF + embedding retrieval
            hybrid ranking
            confidence gate
            category mapping
            KB-only resolution draft
            grounding verifier
            duplicate matching
            no-match gap clustering
```

## Pipeline

```text
Raw Ticket
  ↓
Normalizer and PII Redactor
  ↓
Field Extractor + Missing Information Detector
  ↓
TF-IDF Retrieval + Optional Embedding Retrieval
  ↓
Hybrid Top-3 Ranker
  ↓
Confidence / Conflict / Completeness Gate
  ├── weak evidence → NO_RELIABLE_MATCH
  ├── ambiguous/missing information → NEEDS_ANALYST_REVIEW
  └── sufficient evidence → continue
  ↓
Category + Subcategory Mapper
  ↓
KB-only Source-tagged Resolution Draft Generator
  ↓
Step-Level Grounding Verifier
  ↓
Angular Analyst Review, Edit, Approve/Reject, Feedback
  ↓
MySQL/MongoDB Audit + Evaluation + Knowledge Intelligence
```

---

# INITIALIZE A NEW PROJECT FROM SCRATCH

## Create the root repository

Create a new Git repository. Do not initialize from an upstream repository as the TicketIQ repository.

```bash
mkdir ticketiq
cd ticketiq
git init
mkdir backend frontend ai-service data docs tests presentation scripts
```

Create these root files:

```text
README.md
LICENSE
ATTRIBUTION.md
SECURITY.md
.gitignore
.env.example
docker-compose.yml
MASTER_PROMPT.md
```

## Required root layout

```text
ticketiq/
├── README.md
├── LICENSE
├── ATTRIBUTION.md
├── SECURITY.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── MASTER_PROMPT.md
├── docs/
│   ├── architecture.md
│   ├── api-contract.md
│   ├── data-dictionary.md
│   ├── prompt-catalog.md
│   ├── testing-strategy.md
│   ├── evaluation-report.md
│   ├── user-manual.md
│   ├── demo-script.md
│   └── ai-sdlc-evidence.md
├── backend/
├── frontend/
├── ai-service/
├── data/
│   ├── seed/
│   ├── generated/
│   └── synthetic-data-generator/
├── tests/
│   ├── playwright/
│   └── api/
├── presentation/
└── scripts/
```

Make an initial commit:

```bash
git add .
git commit -m "chore: initialize TicketIQ monorepo"
```

---

# BACKEND IMPLEMENTATION — JAVA 21 / SPRING BOOT 3.3 / GRADLE

## Generate backend

Create `backend/` as a fresh Gradle Spring Boot project.

### Dependencies

Use only needed stable dependencies compatible with Spring Boot 3.3.x:

- Spring Boot Starter Web
- Spring Boot Starter Validation
- Spring Boot Starter Data JPA
- Spring Boot Starter Data MongoDB
- Spring Boot Starter Security only if login/RBAC is completed; otherwise seed a simple demo analyst role
- MySQL Connector/J
- Liquibase or Flyway for MySQL schema migrations; select one and use it consistently
- Lombok only if the team is comfortable maintaining it
- Springdoc OpenAPI/Swagger compatible with Spring Boot 3.3
- Spring Boot Starter Test
- JUnit 5
- Mockito
- Testcontainers only if environment supports Docker; otherwise provide test profiles with embedded/mocked dependencies

### Java package layout

```text
backend/src/main/java/com/ticketiq/
├── TicketIqApplication.java
├── config/
├── controller/
├── dto/
├── entity/
├── repository/
├── service/
├── integration/
│   └── ai/
├── rules/
├── security/
├── audit/
├── exception/
└── mapper/
```

### Required backend modules

1. Ticket CRUD and lifecycle.
2. Knowledge article management/seed endpoints.
3. AI service client using typed DTOs and timeouts.
4. Ticket analysis orchestration service.
5. Analyst edit/approval/rejection workflow.
6. Feedback service.
7. Evaluation-run service.
8. Dashboard metrics service.
9. Batch CSV upload/job/export service, only after core flow works.
10. Audit event service.

### Required ticket statuses

```text
DRAFT
SUBMITTED
ANALYZING
ANALYZED
NEEDS_ANALYST_REVIEW
NO_RELIABLE_MATCH
APPROVED
REJECTED
```

### Required decision statuses

```text
DRAFT_ALLOWED
NEEDS_MORE_INFORMATION
NEEDS_ANALYST_REVIEW
NO_RELIABLE_MATCH
```

### Backend API endpoints

```text
POST   /api/tickets
GET    /api/tickets
GET    /api/tickets/{ticketId}
PUT    /api/tickets/{ticketId}

POST   /api/tickets/{ticketId}/analyze
POST   /api/tickets/{ticketId}/approve
POST   /api/tickets/{ticketId}/reject
POST   /api/tickets/{ticketId}/feedback
GET    /api/tickets/{ticketId}/duplicates
GET    /api/tickets/{ticketId}/evidence
GET    /api/tickets/{ticketId}/audit

GET    /api/knowledge-articles
POST   /api/knowledge-articles
PUT    /api/knowledge-articles/{articleId}

GET    /api/dashboard/metrics
GET    /api/dashboard/knowledge-gaps
GET    /api/dashboard/knowledge-health

POST   /api/batch/analyze
GET    /api/batch/{jobId}
GET    /api/batch/{jobId}/export

POST   /api/evaluation/run
GET    /api/evaluation/results
```

### Critical implementation rules

- Validate all incoming request payloads.
- Implement global exception handling returning a consistent error DTO.
- Use pagination for ticket lists when possible.
- Use typed DTOs; do not expose JPA entities directly.
- Use transactions for approval/feedback/audit writes.
- AI service failure must result in a recoverable status and clear UI error—not a server crash.
- Use timeouts and a fallback error message for AI calls.
- No secret values in `application.yml`; use environment variables and `.env.example`.
- Add Swagger/OpenAPI UI for API demonstration.

---

# DATABASE DESIGN

## MySQL — system of record

Use schema migrations. Required tables:

```text
users
roles
user_roles

tickets
ticket_status_history
ticket_extracted_fields
ticket_classifications
ticket_resolutions
ticket_feedback

categories
subcategories
priority_rules

duplicate_ticket_matches
knowledge_gap_clusters

evaluation_test_cases
evaluation_results

audit_events
```

### Suggested essential fields

```text
tickets:
- id (UUID/string or numeric)
- ticket_number (unique, e.g. INC-1001)
- title
- raw_description (store only synthetic demo data)
- redacted_description
- application_name
- environment
- status
- decision_status
- created_at
- updated_at
- created_by

 ticket_classifications:
- ticket_id
- category_id
- subcategory_id
- confidence
- rationale_json
- model_config_version

 ticket_resolutions:
- ticket_id
- summary
- steps_json
- escalation_json
- grounding_coverage
- analyst_edited
- approved_by
- approved_at

 ticket_feedback:
- ticket_id
- helpful (boolean)
- feedback_text
- category_override
- article_relevance_override_json
- edited_resolution_json
- created_at

 audit_events:
- id
- ticket_id
- actor
- event_type
- payload_json
- created_at
```

## MongoDB — flexible knowledge and AI records

Required collections:

```text
knowledge_articles
knowledge_chunks
ticket_ai_analyses
retrieval_logs
rag_generation_logs
prompt_versions
embedding_metadata
feedback_documents
knowledge_gap_documents
```

### Knowledge article document model

```json
{
  "articleId": "KB-04",
  "title": "Payroll Portal Authentication Failure After Password Reset",
  "category": "Access Management",
  "subcategory": "Password Synchronization",
  "symptoms": [
    "AUTH-401",
    "Login failure after password reset",
    "Multiple users unable to access the portal"
  ],
  "possibleCause": "Directory password synchronization has not completed.",
  "prerequisites": [
    "Use approved identity verification procedure before account-related support."
  ],
  "steps": [
    {
      "sourceStepId": "KB-04-S1",
      "order": 1,
      "text": "Verify directory password synchronization completion for affected users."
    },
    {
      "sourceStepId": "KB-04-S2",
      "order": 2,
      "text": "Ask users to clear stored portal credentials and sign in again."
    }
  ],
  "validation": "Affected users can sign in without AUTH-401.",
  "escalationCondition": "Escalate to Identity Operations if more than five users remain affected after synchronization validation.",
  "keywords": ["AUTH-401", "password reset", "login", "payroll"],
  "version": "1.0",
  "reviewDate": "2026-10-01",
  "synthetic": true
}
```

---

# PYTHON AI SERVICE — FASTAPI

## Create isolated environment

```bash
cd ai-service
python -m venv .venv
# activate according to operating system
python -m pip install --upgrade pip
```

## Suggested requirements

```text
fastapi
uvicorn[standard]
pydantic
scikit-learn
numpy
pandas
regex
python-multipart
sentence-transformers   # optional/recommended when environment permits
pytest
httpx
```

Add only libraries you actually use. Pin versions after validating compatibility with Python 3.13.

## AI-service layout

```text
ai-service/
├── requirements.txt
├── README.md
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routers/
│   │   ├── health.py
│   │   ├── analysis.py
│   │   ├── evaluation.py
│   │   └── knowledge.py
│   ├── schemas/
│   ├── services/
│   │   ├── redaction_service.py
│   │   ├── normalizer_service.py
│   │   ├── extraction_service.py
│   │   ├── tfidf_retriever.py
│   │   ├── embedding_retriever.py
│   │   ├── hybrid_ranker.py
│   │   ├── confidence_gate.py
│   │   ├── classifier_service.py
│   │   ├── draft_generator.py
│   │   ├── grounding_verifier.py
│   │   ├── duplicate_service.py
│   │   ├── knowledge_gap_service.py
│   │   └── evaluation_service.py
│   ├── prompts/
│   ├── data_access/
│   └── utils/
└── tests/
```

## Required FastAPI endpoints

```text
GET  /health
POST /ai/analyze-ticket
POST /ai/redact
POST /ai/retrieve-knowledge
POST /ai/generate-resolution
POST /ai/verify-grounding
POST /ai/find-duplicates
POST /ai/detect-knowledge-gaps
POST /ai/evaluate
```

## Main analyze endpoint contract

### Request

```json
{
  "ticketId": "INC-1008",
  "ticketText": "Payroll staff cannot log in after password reset. AUTH-401. About 18 users are affected.",
  "structuredFields": {
    "application": "Payroll Portal",
    "environment": "Production"
  },
  "topK": 3,
  "confidenceThreshold": 0.62,
  "retrievalMode": "hybrid"
}
```

### Response

```json
{
  "decision": "DRAFT_ALLOWED",
  "redactedText": "Payroll staff cannot log in after password reset. AUTH-401. About 18 users are affected.",
  "extractedFields": {
    "application": "Payroll Portal",
    "errorCode": "AUTH-401",
    "affectedUsers": 18,
    "trigger": "Password reset"
  },
  "missingFields": [
    "Browser/client version",
    "Whether all user roles are affected"
  ],
  "classification": {
    "category": "Access Management",
    "subcategory": "Password Synchronization",
    "confidence": 0.91,
    "alternatives": []
  },
  "evidence": [
    {
      "articleId": "KB-04",
      "title": "Payroll Portal Authentication Failure After Password Reset",
      "score": 0.89,
      "tfidfScore": 0.82,
      "embeddingScore": 0.91,
      "sharedEvidence": ["AUTH-401", "password reset", "cannot log in"],
      "sourceExcerpt": "Users may see AUTH-401 after a directory password update."
    }
  ],
  "confidence": {
    "finalScore": 0.87,
    "retrievalRelevance": 0.89,
    "ticketCompleteness": 0.75,
    "sourceAgreement": 0.94,
    "groundingCoverage": 1.0,
    "rationale": ["Top article matches error code and reset trigger."]
  },
  "resolutionSteps": [
    {
      "stepNumber": 1,
      "instruction": "Verify directory password synchronization completion for affected users.",
      "sourceArticleId": "KB-04",
      "sourceSection": "Resolution Steps",
      "sourceStepId": "KB-04-S1",
      "verificationStatus": "SUPPORTED"
    }
  ],
  "escalation": {
    "required": true,
    "condition": "Escalate to Identity Operations if more than five users remain affected after synchronization validation.",
    "sourceArticleId": "KB-04",
    "sourceSection": "Escalation Condition"
  },
  "possibleDuplicates": [],
  "configuration": {
    "retrievalMode": "hybrid",
    "threshold": 0.62,
    "promptVersion": "resolution-v1"
  }
}
```

---

# AI PIPELINE IMPLEMENTATION DETAILS

## 1. PII redaction

Implement deterministic redaction first. Use regex and conservative patterns. Preserve error codes where possible.

### Redact

- Email addresses
- Phone numbers
- Password markers and adjacent secret values
- Bearer tokens/API keys/long token-looking sequences
- IPv4 addresses
- URLs/internal hostnames
- Employee/customer IDs only when synthetic pattern is known

### Output format

```text
[REDACTED_EMAIL]
[REDACTED_PHONE]
[REDACTED_SECRET]
[REDACTED_TOKEN]
[REDACTED_IP]
[REDACTED_URL]
[REDACTED_ID]
```

### Rules

- Display raw and redacted view only because all data is fictional; label the raw view as demo-only.
- Send only redacted text to embedding/LLM workflows.
- Add unit tests for every redaction pattern.

## 2. Normalization

- Lowercase for retrieval copy while retaining display original/redacted text.
- Collapse whitespace.
- Normalize common aliases, e.g., `sign-in` → `login`, only if rule is documented.
- Normalize error codes, e.g., `auth 401` → `AUTH-401` where safe.
- Remove repeated boilerplate.

## 3. Field extraction and missing information

Use deterministic extraction first where possible:

- Error code regex.
- User counts: numeric phrases.
- Time phrases.
- Application names from configured catalog.
- Environment values from configured list.

Generate missing-field questions from a required field configuration. Limit to three useful questions.

Example missing fields:

```text
- Which environment is affected: production, test, or development?
- Is the issue affecting all users or selected roles?
- What client/browser version is being used?
```

## 4. Retrieval levels

### Level 1 — TF-IDF baseline

Build article search text using:

```text
title + symptoms + possibleCause + prerequisites + steps + escalationCondition + keywords
```

- Use `TfidfVectorizer`.
- Use cosine similarity.
- Return top three articles.
- Store token-overlap/shared-evidence metadata for UI highlighting.

### Level 2 — embedding retrieval

Use a compatible pretrained sentence-transformers model if it runs locally. Do not train it.

- Encode article search text and ticket redacted text.
- Compute cosine similarity.
- Cache article embeddings.
- Provide a feature/config flag to disable embeddings and run TF-IDF only.

### Level 3 — hybrid ranking

Use a deterministic formula, configurable in one file:

```python
HYBRID_TFIDF_WEIGHT = 0.45
HYBRID_EMBEDDING_WEIGHT = 0.45
ERROR_CODE_EXACT_MATCH_BONUS = 0.10
```

Document how the values are selected from development data. Do not tune on held-out test data.

## 5. Confidence gate

Build a deterministic decision rule.

```python
if top_score < threshold:
    decision = "NO_RELIABLE_MATCH"
elif conflict_between_top_categories:
    decision = "NEEDS_ANALYST_REVIEW"
elif critical_missing_fields:
    decision = "NEEDS_MORE_INFORMATION"
else:
    decision = "DRAFT_ALLOWED"
```

Use a config file for:

```text
NO_MATCH_THRESHOLD
AMBIGUITY_MARGIN
MIN_TICKET_COMPLETENESS
```

## 6. Classifier

Baseline classification must be article-derived:

```text
best matching article → category + subcategory
```

Optional: return alternative categories from top ranked articles. Do not market this as a separately trained classifier unless one is actually trained and evaluated.

## 7. Draft generator

### Preferred baseline

Generate ordered resolution steps directly from the best article, not from a free-form LLM. This is safest and easiest to verify.

### Optional LLM rephrasing

Use an LLM only after sources are selected. The LLM must receive exact selected article steps and return structured JSON that preserves source IDs. If LLM fails or returns invalid schema, fall back to source text without LLM rephrasing.

### Draft generator rule

Every output step must reference an existing `sourceArticleId` and `sourceStepId`.

## 8. Grounding verifier

Validate every output resolution step:

1. Confirm article ID exists in retrieved results.
2. Confirm source step ID exists in that article.
3. Confirm generated text is identical to, safely paraphrases, or semantically matches source text.
4. Flag unsupported steps.
5. Calculate grounding coverage:

```text
grounding_coverage = supported_steps / total_steps
```

If coverage is less than 1.0, do one of:

- remove unsupported step and show warning, or
- change decision to `NEEDS_ANALYST_REVIEW`.

Do not silently claim all steps are grounded.

## 9. Duplicate detection

Use hybrid similarity against synthetic historical tickets.

- Store threshold separately from KB match threshold.
- Return ticket ID, similarity score, previous category, outcome, and KB article used.
- Never auto-link, auto-close, or auto-merge tickets.

## 10. Knowledge-gap clustering

For tickets with `NO_RELIABLE_MATCH`:

- Store redacted text and key terms.
- Cluster with TF-IDF/KMeans or similarity connected-components, depending on small dataset size.
- Show cluster title derived from frequent non-stopword terms.
- Recommend a new article topic for **human review only**.
- Optionally use LLM to draft only an article skeleton, clearly marked as unapproved.

---

# FRONTEND IMPLEMENTATION — ANGULAR

## Bootstrap frontend

Create a fresh Angular application inside `frontend/` using an Angular version compatible with Node 22 in the actual environment.

Use:

- TypeScript strict mode
- Angular routing
- Reactive forms
- Angular Material or PrimeNG; choose one and keep design consistent
- HTTP interceptors for errors/loading if useful
- Feature-oriented folder structure

## Frontend structure

```text
frontend/src/app/
├── core/
│   ├── api/
│   ├── guards/
│   ├── interceptors/
│   └── services/
├── shared/
│   ├── components/
│   ├── models/
│   ├── pipes/
│   └── utils/
├── layouts/
│   └── main-layout/
└── features/
    ├── dashboard/
    ├── tickets/
    ├── knowledge-base/
    ├── duplicates/
    ├── knowledge-gaps/
    ├── evaluation/
    ├── feedback/
    └── batch-triage/
```

## Required screens

### 1. Operations dashboard

Show:

- Total tickets
- Tickets analyzed
- Draft allowed / no-match / needs-review count
- Top recurring categories
- No-match clusters
- KB health warnings
- Recent analyst feedback

### 2. Ticket intake

Fields:

- Ticket number
- Title
- Free-text description
- Application/service
- Error message/code
- Affected users
- Start time
- Environment
- Business impact
- Contact channel

Actions:

- Save draft
- Analyze ticket
- Reset

### 3. Ticket analysis workspace

Use a three-column desktop layout or responsive tabs:

```text
Ticket Details | AI Analysis | Evidence and Resolution
```

Include:

- Raw/demo and redacted text preview
- Missing details and clarifying questions
- Category/subcategory badge
- Confidence/Evidence Decision Card
- Top-three article cards with similarity scores
- Shared-evidence highlighting
- Source-tagged numbered resolution steps
- Escalation card
- Duplicate-ticket panel
- Analyst editing controls
- Helpful/not helpful feedback
- Approve/reject controls
- Audit history link

### 4. Knowledge-base manager

- List seeded knowledge articles
- Read article details
- Show category, steps, escalation condition, version, review date
- Create/update fictional articles only

### 5. Evaluation dashboard

- Category accuracy
- Subcategory accuracy
- Top-1/top-3 retrieval hit rate
- No-match precision/recall
- False-refusal rate
- Grounding coverage
- Confusion matrix
- TF-IDF vs embeddings vs hybrid comparison
- Threshold slider/trade-off panel
- Evaluation run timestamp and configuration version

### 6. Knowledge-gap dashboard

- No-match clusters
- Cluster size
- representative tickets (redacted)
- common terms
- suggested future KB topic
- review status

### 7. Optional batch triage screen

- CSV upload
- Result table
- Export download

## UI design system

- Professional IT-operations style; no giant decorative chatbot screen.
- Primary: navy/indigo.
- Success/verified: green.
- Analyst attention/uncertain: amber.
- Escalation/critical: red.
- Use visible status chips: `Grounded`, `Needs Review`, `No Reliable Match`, `Escalation Required`.
- Ensure keyboard navigation, readable contrast, loading states, empty states, and clear error messages.

---

# API CONTRACT INTEGRATION

## Angular → Spring Boot

Use Spring Boot as the frontend’s only backend entry point. Angular should not call the Python AI service directly.

```text
Angular → Spring Boot → Python AI service
```

## Spring Boot → FastAPI

- Use typed request/response DTOs.
- Configure base URL using environment variable.
- Use timeout/retry strategy appropriate for prototype.
- Log correlation/ticket ID; never log unredacted sensitive values.
- On AI service failure, return a clear error and maintain ticket state safely.

## Response shape rule

Use one versioned analysis response DTO. Do not allow frontend-specific random JSON shapes.

---

# SYNTHETIC DATA GENERATION

## Required dataset

Create:

- 12–15 fictional knowledge-base articles.
- 25–30 fictional tickets.
- 4–6 categories and subcategories.
- 5–6 deliberate no-match tickets.
- Expected result labels for every ticket.
- 10 expected test records at minimum.

## Suggested categories

```text
Access Management
Performance and Availability
Batch Processing
Interface and Integration
Data and Reporting
```

## Ticket distribution

```text
8  complete/clear tickets
5  paraphrased tickets
5  incomplete or vague tickets
4  ambiguous tickets
4  duplicate/similar tickets
2  high-impact tickets
5–6 deliberate no-match tickets
```

## Dataset rules

- Use fictional product/system names such as Payroll Portal, Northstar ERP, Atlas VPN, Orion Batch Scheduler.
- Use fictional users and fake error codes.
- Do not use copied internal/runbook data.
- Include expected category, subcategory, expected article or none, expected decision, expected missing fields, and duplicate relationship where relevant.

## Example ticket test record

```json
{
  "ticketId": "INC-1012",
  "title": "Nightly export failed",
  "description": "Nightly customer export failed with BATCH-204 after the scheduler ran.",
  "expectedCategory": "Batch Processing",
  "expectedSubcategory": "Scheduled Job Failure",
  "expectedArticleId": "KB-06",
  "expectedDecision": "DRAFT_ALLOWED",
  "expectedMissingFields": ["Previous successful job run"],
  "isNoMatch": false
}
```

## Prompt logging

If an LLM helps create synthetic variants, preserve the prompt and manually review every output. Store prompts in `docs/prompt-catalog.md`.

---

# EVALUATION PLAN

## Split before tuning

- Development set: approximately 60%.
- Held-out test set: approximately 40%.

Tune retrieval weights and thresholds only on the development set. Freeze them before running final held-out test evaluation.

## Metrics

```text
Category accuracy
Subcategory accuracy
Top-1 retrieval hit rate
Top-3 retrieval hit rate
No-match precision
No-match recall
False-refusal rate
Duplicate precision/recall if implemented
Grounding coverage
PII redaction test coverage
Analyst acceptance rate (synthetic/demo feedback)
```

## Threshold tuning procedure

1. Run development tickets.
2. Record top retrieval score for known-match and no-match tickets.
3. Test multiple candidate thresholds.
4. Choose threshold based on the desired safety/coverage trade-off.
5. Lock threshold and hybrid weights in config.
6. Run held-out test set once.
7. Store and display actual results.

## Required dashboard statement

Display:

> “Metrics are based on a small synthetic held-out test set and are indicative prototype results, not production performance claims.”

---

# TESTING REQUIREMENTS

## Backend tests

- Ticket service behavior.
- Validation failures.
- AI client success/failure handling.
- Approval/rejection workflow.
- Feedback persistence.
- Audit record creation.
- Evaluation-run persistence.

## AI-service unit tests

- Email/phone/IP/secret/token/URL redaction.
- Normalization.
- TF-IDF top-k retrieval.
- Hybrid-ranking deterministic score.
- No-match gate thresholds.
- Ambiguity rule.
- Category mapping.
- Grounding verifier.
- Duplicate matcher.
- Knowledge-gap clusterer.

## Playwright tests

Create tests in Python. Required scenarios:

1. **Known ticket**: ticket analysis returns expected category, articles, and source-tagged steps.
2. **PII redaction**: email/password/IP input becomes redacted in analysis preview.
3. **No-match safety**: unknown ticket returns `No Reliable Match` with no unsupported technical steps.
4. **Duplicate detection**: similar ticket displays synthetic historical ticket candidate.
5. **Analyst approval**: edited resolution persists and audit history records decision.
6. **Knowledge-gap dashboard**: recurring no-match cluster is visible.

Take screenshots on test success/failure where appropriate for presentation evidence.

---

# DOCUMENTATION DELIVERABLES

## README.md

Must include:

- Problem and solution.
- Features.
- Architecture diagram.
- Tech stack.
- Repository setup.
- Environment variables.
- How to load synthetic data.
- How to run backend, frontend, AI service, and tests.
- Screenshots.
- API documentation location.
- Evaluation summary with actual results.
- Limitations and safety notes.
- Attribution.

## docs/architecture.md

Include C4-lite diagrams or Mermaid diagrams for:

- Context.
- Container architecture.
- Analysis pipeline.
- Data flow.

## docs/user-manual.md

Include step-by-step screenshots/instructions for:

- Creating a ticket.
- Reviewing PII redaction.
- Running analysis.
- Reading sources/confidence.
- Editing/approving results.
- Giving feedback.
- Using evaluation and gap dashboards.

## docs/prompt-catalog.md

For each prompt:

```text
Prompt ID
Version
Purpose
Input schema
Prompt text/template
Output schema
Safety constraints
Known limitations
Test cases
Owner
Last updated date
```

## docs/ai-sdlc-evidence.md

Document responsible AI use for:

- Synthetic data generation.
- Test generation.
- Code review.
- Documentation drafting.
- UI ideation.

State that all AI-produced material was reviewed by team members.

## docs/evaluation-report.md

Include:

- Dataset makeup.
- Split method.
- Frozen configuration.
- Dev tuning approach.
- Held-out test results.
- Confusion matrix.
- Errors/edge cases.
- Limitations.

---

# SECURITY REQUIREMENTS

Create `SECURITY.md` describing:

- Synthetic data only.
- No secrets committed.
- `.env.example` contains placeholders only.
- PII redaction happens before AI processing.
- No live external ITSM/system access.
- Human approval is required.
- Dependency checks should be run if time/environment allows.
- Reported security issues should not be placed in public issue content during the hackathon.

Use `.gitignore` for:

```text
.env
*.env
.venv/
node_modules/
dist/
build/
.gradle/
.idea/
.project
.classpath
.settings/
__pycache__/
.pytest_cache/
coverage/
playwright-report/
test-results/
*.log
```

---

# DOCKER COMPOSE — OPTIONAL BUT RECOMMENDED

If Docker is supported by the lab, add a `docker-compose.yml` for:

- MySQL
- MongoDB
- Backend
- AI service
- Frontend

If Docker is unavailable, provide simple independent startup commands and scripts.

Never make Docker a hard dependency for the demo if the lab environment may not support it.

---

# DEVELOPMENT SEQUENCE AND GIT COMMITS

Do not attempt every feature at once. Build and verify in this order.

## Milestone 0 — Repo and environment

- Create clean monorepo.
- Add attribution, license, security, gitignore, docs placeholders.
- Validate Java, Gradle, Node, Angular CLI, Python, MySQL, MongoDB setup.

Commit:

```text
chore: initialize TicketIQ monorepo and documentation
```

## Milestone 1 — Data and backend foundations

- Create synthetic KB/tickets/expected labels.
- Implement MySQL schema migrations.
- Implement MongoDB knowledge documents.
- Implement ticket CRUD and article seed loading.

Commit:

```text
feat: add ticket and knowledge base data foundations
```

## Milestone 2 — Baseline vertical slice

- Implement Python PII redaction.
- Implement TF-IDF retrieval/top three.
- Implement threshold/no-match decision.
- Map best article to category/subcategory.
- Implement source-step resolution draft from KB.
- Integrate Spring Boot to FastAPI.
- Build Angular ticket intake and evidence display.

Commit:

```text
feat: add evidence-gated ticket analysis baseline
```

## Milestone 3 — Analyst workflow

- Add missing-information display.
- Add editable draft.
- Add approve/reject/feedback flow.
- Add audit history.

Commit:

```text
feat: add analyst review and feedback workflow
```

## Milestone 4 — Verification and quality

- Add grounding verifier.
- Add evaluation runner/dashboard.
- Create dev/test split.
- Tune threshold on dev data.
- Run held-out test evaluation.
- Add backend/AI unit tests.
- Add Playwright core flow tests.

Commit:

```text
feat: add grounding verification and evaluation dashboard
```

## Milestone 5 — Winning differentiators

- Add embedding/hybrid retrieval comparison.
- Add duplicate detection.
- Add knowledge-gap clustering.
- Add KB health monitor.
- Add threshold trade-off slider.

Commit:

```text
feat: add TicketIQ knowledge intelligence features
```

## Milestone 6 — Polish and deliverables

- Add optional batch mode only if all prior milestones work.
- Finalize UI consistency, empty/error/loading states.
- Finalize README, user manual, architecture, prompts, evaluation report.
- Produce presentation/demo screenshots.
- Run final regression tests.

Commit:

```text
docs: finalize hackathon delivery assets and validation evidence
```

---

# DO NOT BUILD THESE UNTIL CORE IS COMPLETE

Avoid scope creep. Do not prioritize:

- Live Jira/ServiceNow/Freshservice integration.
- Automatic remediation or command execution.
- Kubernetes.
- Complex authentication/SSO.
- A separate mobile application.
- Voice input.
- Elaborate animation.
- Training a model from scratch.
- Autonomous multi-agent systems without measurable benefit.
- Multilingual support without a labeled evaluation set.

---

# DEMO PLAN

## Five-minute flow

### 0:00–0:35 — Problem

“Support analysts must interpret vague tickets and search scattered knowledge articles. Generic AI can invent unsafe answers. TicketIQ retrieves approved evidence, validates it, and keeps the analyst in control.”

### 0:35–1:35 — Known ticket

- Enter ticket with an authentication issue.
- Show PII redaction preview.
- Show category/subcategory, confidence card, top three articles, source excerpts, grounded steps, and escalation rule.

### 1:35–2:10 — Paraphrase

- Enter a differently worded version.
- Show semantic/hybrid retrieval successfully finding the same article.

### 2:10–2:50 — Incomplete or ambiguous ticket

- Show missing information and `NEEDS_ANALYST_REVIEW`.
- Demonstrate that the system does not pretend certainty.

### 2:50–3:25 — No-match safety

- Enter unknown error scenario.
- Show `No Reliable Match` and safe information-collection checklist.

### 3:25–4:10 — Human value

- Show edit/approve/audit workflow.
- Show duplicate panel.

### 4:10–4:40 — Improvement loop

- Show no-match cluster and suggested KB topic.
- Show article health/feedback signal.

### 4:40–5:00 — Proof

- Show evaluation dashboard and Playwright passing report.
- Close with the core statement.

## Closing statement

> “TicketIQ does not use AI to guess a fix. It proves where every recommendation came from, refuses unsupported answers, and turns analyst feedback and unresolved tickets into continuous knowledge-base improvement.”

---

# JUDGE QUESTION ANSWERS

## Why not use only an LLM?

An LLM can generate plausible but unsupported operational instructions. TicketIQ uses controlled retrieval, source tags, a confidence gate, and a grounding verifier. It only drafts actions tied to approved KB steps.

## How do you validate accuracy?

We use labeled synthetic tickets and articles, separate development/test data, tune only on development data, freeze configuration, and report actual held-out metrics: category accuracy, top-1/top-3 retrieval hit rate, no-match performance, false refusals, and grounding coverage.

## What happens if the knowledge base is missing information?

TicketIQ returns `No Reliable Match` instead of guessing. Repeated no-match patterns become a knowledge-gap cluster and proposed article topic for human SME review.

## Is it safe?

Only fictional data is used; sensitive patterns are redacted before AI processing; TicketIQ cannot execute changes; every draft requires human approval; and the system maintains an audit trail.

## How does it scale?

The architecture keeps the same API contracts. A future deployment can replace local retrieval with a governed vector database, ingest approved documentation, add SSO/RBAC, connect to ITSM through reviewed APIs, and monitor retrieval/feedback quality continuously.

---

# DEFINITION OF DONE

Do not call the project complete until every applicable item is checked.

```text
[ ] Fresh TicketIQ repository exists; it is not merely a fork.
[ ] Upstream references were audited and documented in ATTRIBUTION.md.
[ ] Backend uses Java 21, Gradle 8.x, and Spring Boot 3.3.x.
[ ] Frontend runs on Node 22-compatible Angular.
[ ] Python 3.13 FastAPI service runs in a virtual environment.
[ ] MySQL and MongoDB are used for their defined roles.
[ ] Only synthetic KB articles/tickets are stored.
[ ] Ticket text is redacted before AI retrieval/generation.
[ ] Top-three article retrieval works.
[ ] Category/subcategory and rationale are displayed.
[ ] Weak evidence triggers No Reliable Match.
[ ] Each resolution step cites a real KB source step.
[ ] Grounding verifier validates citations.
[ ] Analyst can edit, approve/reject, and give feedback.
[ ] Audit events are saved.
[ ] Duplicate detection works, if included.
[ ] Knowledge-gap dashboard works, if included.
[ ] Evaluation uses dev/test split and real computed values.
[ ] Evaluation dashboard shows metrics and limitations.
[ ] Unit/API tests pass.
[ ] Playwright E2E tests pass.
[ ] README, architecture diagram, user manual, prompt log, testing strategy, and demo script are complete.
[ ] Presentation/demo assets are ready.
[ ] No credentials, private data, or secrets are committed.
```

---

# FINAL INSTRUCTION TO THE CODING AGENT

Build TicketIQ iteratively. Begin by reading this entire file, auditing reference repositories only if they are actually needed, and creating a new clean repository with the exact required stack. Implement the baseline vertical slice before optional features. After each milestone:

1. Run relevant tests.
2. Fix failures before adding features.
3. Make a meaningful Git commit.
4. Update documentation.
5. Keep the UI consistent with the TicketIQ design system.
6. Preserve source attribution and never commit secrets.

When a decision is ambiguous, choose the simpler implementation that is fully testable, explainable, and demo-ready. Prioritize **evidence, verification, safety, and polish** over feature count.
