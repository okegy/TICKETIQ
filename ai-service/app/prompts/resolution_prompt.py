"""
Resolution prompt templates — v1.

These templates are used to structure the resolution draft generation
rationale displayed to the analyst. They are NOT sent to any LLM; they
provide a structured header for the evidence-grounded steps shown in the
TicketIQ Command Center.

Each template returns a plain-text preamble that prefixes the resolution
steps rendered in the frontend.
"""

from typing import Any

RESOLUTION_HEADER_TEMPLATE = """
TICKETIQ EVIDENCE-GATED RESOLUTION DRAFT
=========================================
Ticket         : {ticket_id}
Classification : {category} / {subcategory}
Top Article    : [{article_id}] {article_title}
Confidence     : {confidence:.0%}
Decision       : {decision}
Threshold      : {threshold:.0%}
Generated      : {timestamp}

IMPORTANT: All resolution steps below are sourced exclusively from the
approved Knowledge Base article referenced above. Steps lacking a source
reference should not be executed. Analyst review and approval is required
before any action is taken.
""".strip()

NO_MATCH_TEMPLATE = """
TICKETIQ — NO RELIABLE MATCH
=============================
Ticket    : {ticket_id}
Threshold : {threshold:.0%}
Top Score : {top_score:.0%}

The evidence retrieval gate has REFUSED to generate a resolution draft
because the best-matching knowledge article scored {top_score:.0%}, which is
below the configured safety threshold of {threshold:.0%}.

RECOMMENDED ACTION: Escalate this ticket to Tier-2 Service Desk for manual
triage. Do not attempt to resolve without an approved knowledge article.
""".strip()


def build_resolution_header(
    ticket_id: str,
    category: str,
    subcategory: str,
    article_id: str,
    article_title: str,
    confidence: float,
    decision: str,
    threshold: float,
) -> str:
    """Return the evidence-grounded resolution header preamble."""
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return RESOLUTION_HEADER_TEMPLATE.format(
        ticket_id=ticket_id,
        category=category,
        subcategory=subcategory,
        article_id=article_id,
        article_title=article_title,
        confidence=confidence,
        decision=decision,
        threshold=threshold,
        timestamp=ts,
    )


def build_no_match_message(
    ticket_id: str,
    threshold: float,
    top_score: float,
) -> str:
    """Return the refusal message for sub-threshold tickets."""
    return NO_MATCH_TEMPLATE.format(
        ticket_id=ticket_id,
        threshold=threshold,
        top_score=top_score,
    )
