"""
Priority and urgency rules engine — deterministic, keyword-based.

No ML inference. Every decision is traceable to a keyword match or
the P4 default rule. Complies with the TicketIQ design requirement
for fully explainable, zero-hallucination prioritisation.

Priority levels : P1 (Critical) > P2 (High) > P3 (Medium) > P4 (Low)
Urgency labels  : CRITICAL | HIGH | MEDIUM | LOW
"""

import re
from typing import Any

# ── Keyword rule sets (first match wins) ─────────────────────────────────────

_P1_KEYWORDS = [
    "production down", "all users", "service unavailable",
    "data loss", "breach", "security incident", "ransomware",
    "database corrupted", "complete outage", "critical failure",
    "system-wide", "entire organisation", "revenue impact",
    "all employees", "entire company"
]

_P2_KEYWORDS = [
    "multiple users", "team unable", "degraded performance",
    "partial outage", "batch job failed", "nightly job",
    "partner api", "integration failure", "major feature",
    "high cpu", "memory leak", "timeout", "escalation required",
    "interface file rejected", "503", "gateway"
]

_P3_KEYWORDS = [
    "single user", "one user", "account locked", "password reset",
    "login loop", "sso", "slow report", "missing dashboard",
    "duplicate record", "blank pdf", "export failed",
    "interface file", "email not received", "can't log in"
]

# P4 is the fall-through default


def _keyword_hit(keyword: str, text: str) -> bool:
    """Whole-word/phrase match so short keywords like 'sso' don't
    fire inside unrelated words ('espresso')."""
    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None


def evaluate_priority(
    ticket_text: str,
    category: str = "",
    subcategory: str = ""
) -> dict[str, Any]:
    """
    Evaluate priority rules for a ticket.

    Args:
        ticket_text: Raw or redacted ticket description.
        category:    Category string from AI classification.
        subcategory: Subcategory string from AI classification.

    Returns:
        dict with keys: priority, urgency, rationale, matchedRules
    """
    combined = f"{ticket_text} {category} {subcategory}".lower()

    for kw in _P1_KEYWORDS:
        if _keyword_hit(kw, combined):
            return {
                "priority": "P1",
                "urgency": "CRITICAL",
                "rationale": f"Keyword '{kw}' indicates a production-wide critical incident.",
                "matchedRules": [f"KEYWORD_MATCH:{kw}", "RULE:P1_CRITICAL"]
            }

    for kw in _P2_KEYWORDS:
        if _keyword_hit(kw, combined):
            return {
                "priority": "P2",
                "urgency": "HIGH",
                "rationale": f"Keyword '{kw}' indicates a high-impact multi-user or integration incident.",
                "matchedRules": [f"KEYWORD_MATCH:{kw}", "RULE:P2_HIGH"]
            }

    for kw in _P3_KEYWORDS:
        if _keyword_hit(kw, combined):
            return {
                "priority": "P3",
                "urgency": "MEDIUM",
                "rationale": f"Keyword '{kw}' indicates a single-user or standard service-desk incident.",
                "matchedRules": [f"KEYWORD_MATCH:{kw}", "RULE:P3_MEDIUM"]
            }

    return {
        "priority": "P4",
        "urgency": "LOW",
        "rationale": "No high-priority keyword matched. Defaulting to standard low-priority queue.",
        "matchedRules": ["RULE:P4_DEFAULT"]
    }
