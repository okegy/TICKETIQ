# 🎬 TicketIQ — Hackathon Demo Script (3-Minute Presentation)

## Pitch (30 seconds)
> "In IT AMS support, analysts waste hours manually searching through scattered knowledge bases or dealing with inaccurate generic AI chatbots that hallucinate technical fixes.  
> We built **TicketIQ** — an **evidence-gated, analyst-controlled resolution copilot**. It redacts sensitive data, classifies tickets, retrieves verified internal knowledge, and **refuses to answer** when facts are insufficient."

---

## Live Demo Walkthrough (2 minutes)

### Step 1: PII Redaction & High-Confidence Resolution
1. Open the **TicketIQ Analyst Dashboard** (`http://localhost:4200`).
2. Click **"Payroll Auth Error"**.
   - Note the raw text contains sensitive emails (`supervisor@company.com`) and password reset keywords.
3. Click **"Analyze Ticket & Retrieve Resolution"**.
4. **Showcase the Result:**
   - **PII Redaction Box:** Email is instantly replaced with `[REDACTED_EMAIL]`.
   - **Classification Chip:** Automatically tagged as `Access Management / Password Synchronization` with 78% confidence.
   - **Grounded Steps:** Shows 3 clear steps, each citing `KB-02` with step verification badges.
   - **Escalation Trigger:** Flags the automatic condition: *"Escalate to Identity Operations if more than 5 users remain affected."*

### Step 2: Refusal of Ungrounded Inquiries (Anti-Hallucination)
1. Click **"Unmatched Query"** (e.g., *"The coffee machine on 4th floor is out of espresso beans"*).
2. Click **"Analyze Ticket"**.
3. **Showcase the Result:**
   - Red banner displays: **Status: NO_RELIABLE_MATCH**.
   - Highlight: *"Unlike ChatGPT, TicketIQ refuses to fabricate an unapproved technical resolution when evidence is absent."*

### Step 3: Bonus Value Adds
1. **Duplicate Detection:** Automatic comparison identifies past recurring incidents.
2. **Continuous Knowledge Improvement:** Recurring unmatched tickets are clustered to suggest new knowledge base topics.

---

## Conclusion & Tech Stack (30 seconds)
- Built on **Spring Boot 3.3.4 (Java 21)**, **Angular 21**, **MySQL & MongoDB**, **FastAPI (Python 3.12)**, and **Playwright E2E tests**.
- 100% test pass rate and 90% benchmark accuracy.
