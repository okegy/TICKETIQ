"""
Real threshold evaluation over the labeled ticket set.

Runs the actual pipeline (redaction → retrieval → gate) once per labeled
ticket, records the top score + top article, then sweeps candidate refusal
thresholds analytically. Every number returned here is measured, not
estimated.

Labeled set: ticketiq/data/evaluation/labeled_tickets.json
(same file as the verification kit's tickets_sample.json).
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from app.services.redaction_service import RedactionService
from app.services.tfidf_retriever import TfidfRetriever
from app.services.glossary import build_search_query
from app.services.language_service import detect_language

KB_SEED_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "seed", "knowledge_articles.json"))
LABELED_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "evaluation", "labeled_tickets.json"))

_LONG_TEXT = re.compile(r"LONG_TEXT:\s*repeat '([^']+)' \d+ times")

THRESHOLDS = [round(0.05 + 0.05 * i, 2) for i in range(18)]  # 0.05 … 0.90


class EvaluationService:
    def __init__(self, labeled_path: str = LABELED_PATH, kb_path: str = KB_SEED_PATH):
        self.retriever = TfidfRetriever(kb_path=kb_path)
        self.tickets: List[Dict[str, Any]] = []
        self._run_pipeline(labeled_path)

    def _run_pipeline(self, labeled_path: str) -> None:
        if not os.path.exists(labeled_path):
            return
        with open(labeled_path, "r", encoding="utf-8") as fh:
            labeled = json.load(fh)

        measured = []
        for t in labeled:
            desc: str = t.get("description", "") or ""
            if not desc.strip():
                continue  # empty-input edge cases (E-01/E-03) — validated elsewhere

            m = _LONG_TEXT.search(desc)
            if m:
                desc = (m.group(1) + " ") * 200

            lang = detect_language(desc)
            redacted = RedactionService.redact_text(desc)
            query = build_search_query(redacted, lang)
            retrieved = self.retriever.retrieve(query, top_k=1)
            top_score = retrieved[0]["tfidfScore"] if retrieved else 0.0
            top_article = (retrieved[0].get("articleId") or retrieved[0].get("id")) if retrieved else None

            measured.append({
                "id": t.get("id"),
                "type": t.get("type"),
                "expectMatched": t.get("expect_matched"),
                "expectArticle": t.get("expect_article"),
                "topScore": round(float(top_score), 4),
                "topArticle": top_article,
            })

        self.tickets = measured

    @property
    def size(self) -> int:
        return len(self.tickets)

    def sweep(self) -> Dict[str, Any]:
        """Sweep every candidate threshold and compute the real trade-off."""
        match_scores = [t["topScore"] for t in self.tickets if t["expectMatched"] is True]
        nomatch_scores = [t["topScore"] for t in self.tickets if t["expectMatched"] is False]

        sweep = []
        for thr in THRESHOLDS:
            covered = sum(1 for s in match_scores if s >= thr)
            false_refusals = len(match_scores) - covered
            correct_refusals = sum(1 for s in nomatch_scores if s < thr)
            sweep.append({
                "threshold": thr,
                "coverage": round(100.0 * covered / len(match_scores), 1) if match_scores else 0.0,
                "refusalAccuracy": round(100.0 * correct_refusals / len(nomatch_scores), 1) if nomatch_scores else 0.0,
                "falseRefusals": false_refusals,
                "groundedDrafts": covered,
            })

        # Safe window: thresholds where BOTH coverage and refusal accuracy are 100%.
        full = [s["threshold"] for s in sweep
                if s["coverage"] == 100.0 and s["refusalAccuracy"] == 100.0]
        tuned: Optional[float] = 0.15
        tuned_in_window = any(abs(full[i] - tuned) < 0.026 for i in range(len(full))) if full else False
        if full and not tuned_in_window:
            tuned = full[len(full) // 2]

        return {
            "dataset": {
                "tickets": len(self.tickets),
                "matchExpected": len(match_scores),
                "noMatchExpected": len(nomatch_scores),
            },
            "tunedThreshold": tuned,
            "safeWindow": {"min": min(full), "max": max(full)} if full else None,
            "minMatchedScore": min(match_scores) if match_scores else None,
            "maxUnmatchedScore": max(nomatch_scores) if nomatch_scores else None,
            "sweep": sweep,
        }
