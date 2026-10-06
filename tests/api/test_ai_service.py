"""
API integration tests for TicketIQ AI Service.

Run with:
    cd ticketiq/ai-service
    .venv/Scripts/activate  (Windows) | source .venv/bin/activate (Linux/Mac)
    pytest ../tests/api/test_ai_service.py -v

The AI service must be running on http://127.0.0.1:8000 before running tests.
"""

import pytest
import httpx

BASE = "http://127.0.0.1:8000"
TIMEOUT = 30


# ── Health ────────────────────────────────────────────────────────────────────

def test_health():
    r = httpx.get(f"{BASE}/health", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "TicketIQ" in body["service"]


# ── Knowledge articles catalog ────────────────────────────────────────────────

def test_knowledge_articles_returns_list():
    r = httpx.get(f"{BASE}/ai/knowledge-articles", timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert "articles" in body
    assert isinstance(body["articles"], list)
    assert body["count"] >= 1, "KB seed must contain at least one article"


def test_knowledge_article_has_required_fields():
    r = httpx.get(f"{BASE}/ai/knowledge-articles", timeout=TIMEOUT)
    articles = r.json()["articles"]
    first = articles[0]
    for field in ("articleId", "title", "category", "subcategory", "steps"):
        assert field in first, f"Missing field '{field}' in article"


# ── Ticket analysis — DRAFT_ALLOWED ──────────────────────────────────────────

LOCKOUT_TICKET = {
    "ticketId": "TEST-001",
    "ticketText": "User cannot log in, account locked after too many failed login attempts.",
    "structuredFields": {"application": "Identity Admin Console"},
    "confidenceThreshold": 0.10,
    "retrievalMode": "hybrid"
}

def test_analyze_lockout_returns_draft_allowed():
    r = httpx.post(f"{BASE}/ai/analyze-ticket", json=LOCKOUT_TICKET, timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] == "DRAFT_ALLOWED"
    assert len(body["resolutionSteps"]) > 0
    assert body["classification"]["category"] != "Unassigned"


def test_analyze_lockout_redacts_pii():
    payload = dict(LOCKOUT_TICKET)
    payload["ticketText"] = "Account locked. Contact: admin@corp.com or 555-0199."
    r = httpx.post(f"{BASE}/ai/analyze-ticket", json=payload, timeout=TIMEOUT)
    assert r.status_code == 200
    redacted = r.json()["redactedText"]
    assert "admin@corp.com" not in redacted, "Email not redacted"
    assert "555-0199" not in redacted, "Phone not redacted"


def test_analyze_returns_evidence_list():
    r = httpx.post(f"{BASE}/ai/analyze-ticket", json=LOCKOUT_TICKET, timeout=TIMEOUT)
    body = r.json()
    assert "evidence" in body
    assert len(body["evidence"]) >= 1
    ev = body["evidence"][0]
    assert "articleId" in ev
    assert "score" in ev


def test_resolution_steps_have_source_citation():
    r = httpx.post(f"{BASE}/ai/analyze-ticket", json=LOCKOUT_TICKET, timeout=TIMEOUT)
    steps = r.json()["resolutionSteps"]
    for step in steps:
        assert step.get("sourceArticleId"), "Step missing sourceArticleId"
        assert step.get("verificationStatus") == "SUPPORTED"


# ── Ticket analysis — NO_RELIABLE_MATCH ──────────────────────────────────────

NO_MATCH_TICKET = {
    "ticketId": "TEST-002",
    "ticketText": "The coffee machine on 4th floor is broken and out of espresso beans.",
    "structuredFields": {"application": "Facility Support"},
    "confidenceThreshold": 0.15
}

def test_analyze_nomatch_returns_no_reliable_match():
    r = httpx.post(f"{BASE}/ai/analyze-ticket", json=NO_MATCH_TICKET, timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] == "NO_RELIABLE_MATCH"
    assert len(body["resolutionSteps"]) == 0


def test_nomatch_escalation_is_set():
    r = httpx.post(f"{BASE}/ai/analyze-ticket", json=NO_MATCH_TICKET, timeout=TIMEOUT)
    esc = r.json()["escalation"]
    assert esc["required"] is True
    assert "SYSTEM-REFUSAL" in (esc.get("sourceArticleId") or "")


# ── Duplicate detection ───────────────────────────────────────────────────────

DUP_PAYLOAD = {
    "ticketText": "User cannot log in, account locked after too many failed login attempts",
    "historicalTickets": [
        {
            "id": "INC-1082",
            "title": "Account locked after failed logins",
            "rawDescription": "User cannot log in, account locked after too many failed login attempts",
            "status": "RESOLVED"
        },
        {
            "id": "INC-1045",
            "title": "Password reset email not received",
            "rawDescription": "User did not receive the password reset email",
            "status": "RESOLVED"
        }
    ],
    "threshold": 0.35
}

def test_find_duplicates_returns_match():
    r = httpx.post(f"{BASE}/ai/find-duplicates", json=DUP_PAYLOAD, timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert "duplicates" in body
    assert len(body["duplicates"]) >= 1
    dup = body["duplicates"][0]
    assert "similarityScore" in dup
    assert dup["similarityScore"] > 0.35


# ── Priority rules ────────────────────────────────────────────────────────────

def test_priority_p3_account_lockout():
    r = httpx.post(f"{BASE}/ai/priority", json={
        "ticketText": "Account locked after failed login attempts",
        "category": "Access Management",
        "subcategory": "Account Lockout"
    }, timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert body["priority"] in ("P3", "P2", "P1")  # must not be P4 for lockout


def test_priority_p1_production_down():
    r = httpx.post(f"{BASE}/ai/priority", json={
        "ticketText": "Production down — all users affected",
        "category": "",
        "subcategory": ""
    }, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json()["priority"] == "P1"
    assert r.json()["urgency"] == "CRITICAL"


def test_priority_p4_default():
    r = httpx.post(f"{BASE}/ai/priority", json={
        "ticketText": "Please update my monitor resolution preference",
        "category": "",
        "subcategory": ""
    }, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.json()["priority"] == "P4"


# ── Batch triage ──────────────────────────────────────────────────────────────

SAMPLE_CSV = (
    "ticketId,ticketText,application\n"
    "INC-T001,Account locked after too many failed attempts,Identity Portal\n"
    "INC-T002,Nightly batch job failed during reconciliation step,Batch Scheduler\n"
    "INC-T003,The coffee machine on 4th floor is broken,Facility Support\n"
    "INC-T004,,\n"
)

def test_batch_triage_returns_results():
    files = {"file": ("test_batch.csv", SAMPLE_CSV.encode(), "text/csv")}
    r = httpx.post(
        f"{BASE}/ai/batch-triage",
        files=files,
        data={"confidenceThreshold": "0.15"},
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    body = r.json()
    assert body["totalRows"] == 4
    assert body["processedRows"] == 3  # row 4 is empty → SKIPPED


def test_batch_triage_coffee_machine_no_match():
    files = {"file": ("test_batch.csv", SAMPLE_CSV.encode(), "text/csv")}
    r = httpx.post(
        f"{BASE}/ai/batch-triage",
        files=files,
        data={"confidenceThreshold": "0.15"},
        timeout=TIMEOUT
    )
    results = r.json()["results"]
    coffee_row = next((x for x in results if "coffee" in x.get("redactedText", "").lower()), None)
    assert coffee_row is not None
    assert coffee_row["decision"] == "NO_RELIABLE_MATCH"


# ── Chat ──────────────────────────────────────────────────────────────────────

def test_chat_fallback_lockout():
    r = httpx.post(f"{BASE}/ai/chat", json={
        "avatar": "Atlas",
        "message": "How do I resolve an account lockout?"
    }, timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert len(body["reply"]) > 10  # non-empty response
