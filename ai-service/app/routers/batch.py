"""
Batch CSV triage endpoint.

Accepts a CSV file upload with flexible column naming:
  ticketText (required text) — accepts aliases: body, description, ticket,
    text, issue, query, problem_description, incident_description, details,
    complaint. If a subject/title/summary column also exists, both are
    combined (this matches the team's multilingual ticket datasets whose
    text lives in `subject` + `body`).
  ticketId (optional), application (optional), language (optional — en/hi/ta
    respected when the CSV carries its own language column).

Returns JSON with per-row analysis results including classification,
priority, top evidence article, and decision — suitable for export.
"""

import csv
import io
import os
from typing import Dict, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.services.redaction_service import RedactionService
from app.services.tfidf_retriever import TfidfRetriever
from app.services.language_service import resolve_language
from app.services.glossary import build_search_query
from app.utils.priority_rules import evaluate_priority

router = APIRouter()

KB_SEED_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "seed", "knowledge_articles.json"
)
_retriever = TfidfRetriever(kb_path=os.path.abspath(KB_SEED_PATH))

# Header matching: keys are lower-case with spaces/underscores/hyphens removed.
_SUBJECT_ALIASES = ("subject", "title", "summary", "shortdescription")
_BODY_ALIASES = (
    "tickettext", "body", "ticketdescription", "description", "ticket",
    "text", "issue", "query", "problemdescription", "incidentdescription",
    "details", "complaint", "requestdescription",
)
_ID_ALIASES = ("ticketid", "id", "ticketnumber", "incidentid", "ref")
_APP_ALIASES = ("application", "app", "applicationname", "service", "product")
_LANG_ALIASES = ("language", "lang", "languauge")


def _norm(header: str) -> str:
    return header.strip().lower().replace("_", "").replace(" ", "").replace("-", "")


def _cell(raw_row: Dict[str, str], row_fields: Dict[str, str], aliases) -> str:
    """First non-empty value among the aliased columns, or ''."""
    for a in aliases:
        header = row_fields.get(a)
        if header is None:
            continue
        v = raw_row.get(header)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


@router.post("/batch-triage")
async def batch_triage(
    file: UploadFile = File(...),
    confidenceThreshold: float = Form(default=0.15),
):
    """
    Upload a CSV file; receive back a JSON array of triage results.

    Returns:
        JSON object where `results` contains per row:
          rowIndex, ticketId, decision, priority, urgency,
          category, subcategory, confidence, topArticleId, topArticleTitle,
          redactedText, language, rationale
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    content = await file.read()
    try:
        decoded = content.decode("utf-8-sig")  # handle BOM
    except UnicodeDecodeError:
        decoded = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded))
    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV has no header row.")

    # Normalise every header once: "Ticket Text" / "ticket_text" → "tickettext"
    row_fields: Dict[str, str] = {}
    for h in reader.fieldnames:
        if h is None:
            continue
        n = _norm(h)
        row_fields.setdefault(n, h)  # first occurrence wins

    results = []
    for row_idx, raw_row in enumerate(reader, start=1):
        ticket_id = _cell(raw_row, row_fields, _ID_ALIASES) or f"ROW-{row_idx}"
        application = _cell(raw_row, row_fields, _APP_ALIASES)
        lang_col = _cell(raw_row, row_fields, _LANG_ALIASES)

        subject = _cell(raw_row, row_fields, _SUBJECT_ALIASES)
        body = _cell(raw_row, row_fields, _BODY_ALIASES)
        ticket_text = f"{subject} {body}".strip()

        if not ticket_text:
            results.append({
                "rowIndex": row_idx,
                "ticketId": ticket_id,
                "decision": "SKIPPED",
                "error": "No ticket text found (expected ticketText, body, or description column).",
                "priority": "P4",
                "urgency": "LOW",
                "category": "N/A",
                "subcategory": "N/A",
                "confidence": 0.0,
                "topArticleId": None,
                "topArticleTitle": None,
                "redactedText": "",
            })
            continue

        # Per-row language: explicit column wins, then auto-detection.
        lang = resolve_language(lang_col or "auto", ticket_text)

        # 1. Redact PII
        redacted = RedactionService.redact_text(ticket_text)

        # 2. Retrieval (glossary-bridged for hi/ta)
        search_query = build_search_query(redacted, lang)
        retrieved = _retriever.retrieve(search_query, top_k=3)
        top_score = retrieved[0]["tfidfScore"] if retrieved else 0.0

        if top_score < confidenceThreshold:
            decision = "NO_RELIABLE_MATCH"
            category = "Unassigned"
            subcategory = "No Match"
            top_art_id = None
            top_art_title = None
        else:
            decision = "DRAFT_ALLOWED"
            top_art = retrieved[0]
            category = top_art.get("category", "General IT")
            subcategory = top_art.get("subcategory", "Unclassified")
            top_art_id = top_art.get("articleId") or top_art.get("id")
            top_art_title = top_art.get("title", "")

        # 3. Priority rules
        priority_result = evaluate_priority(redacted, category, subcategory)

        results.append({
            "rowIndex": row_idx,
            "ticketId": ticket_id,
            "application": application,
            "decision": decision,
            "priority": priority_result["priority"],
            "urgency": priority_result["urgency"],
            "priorityRationale": priority_result["rationale"],
            "category": category,
            "subcategory": subcategory,
            "confidence": round(top_score, 3),
            "topArticleId": top_art_id,
            "topArticleTitle": top_art_title,
            "redactedText": redacted,
            "language": lang,
        })

    return JSONResponse(content={
        "totalRows": len(results),
        "processedRows": sum(1 for r in results if r.get("decision") != "SKIPPED"),
        "skippedRows": sum(1 for r in results if r.get("decision") == "SKIPPED"),
        "confidenceThreshold": confidenceThreshold,
        "results": results,
    })
