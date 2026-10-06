# 📖 TicketIQ — User Manual & Operations Guide

## 1. Introduction
TicketIQ assists IT support analysts in diagnosing, classifying, and drafting resolution instructions for incidents. All guidance is grounded exclusively in verified organizational knowledge articles.

## 2. Using the Analyst Copilot Interface

### 2.1 Entering Ticket Details
1. Navigate to `http://localhost:4200` in any modern web browser.
2. In the **"Paste IT Ticket"** box, paste the raw incident description reported by the end-user.
3. (Optional) Provide the **Application Name** (e.g. *Payroll Portal*, *SAP ERP*).
4. Adjust the **Confidence Threshold** slider (default: `0.50`). A higher threshold requires stronger keyword agreement before generating a draft.

### 2.2 Processing & Reviewing the Output
- Click **"Analyze Ticket & Retrieve Resolution"**.
- Review the **Sanitized Text**: Ensure sensitive details (email addresses, phone numbers, passwords) were masked with tokens like `[REDACTED_EMAIL]`.
- Check the **Decision Status**:
  - `DRAFT_ALLOWED`: High-confidence match found. Step-by-step instructions are loaded.
  - `NO_RELIABLE_MATCH`: The issue does not match approved documentation. Forward the ticket for manual tier-2 triage.

### 2.3 Escalation Rules
When specific severity thresholds are met (e.g., more than 5 users affected), an amber alert displays the approved operational escalation procedure.
