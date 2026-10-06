"""
Trained IT-service dataset module.

Loads the multilingual IT support ticket CSV (English bucket, ~16K rows),
builds a TF-IDF retrieval index over subject+body, and derives a
nearest-neighbour "queue" / "type" signal (k-NN majority vote).

Deterministic: fixed sample stride, frozen vectorizer settings. The parsed
sample is cached to data/generated/dataset_en_sample.json so subsequent
service starts skip the 25 MB CSV parse.

Dataset: public synthetic multilingual customer-support ticket dataset
(synthetic, no personal data) — see ATTRIBUTION.md.
"""

import csv
import json
import os
import random
import re
from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_MAX_SAMPLE = 4000
_WS = re.compile(r"\s+")


class DatasetService:
    def __init__(self, csv_path: str, cache_path: str):
        self.rows: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), min_df=2, sublinear_tf=True
        )
        self.matrix = None
        self._load(csv_path, cache_path)
        if self.rows:
            corpus = [
                f"{r['subject']} {r['body']} {' '.join(r['tags'])}" for r in self.rows
            ]
            self.matrix = self.vectorizer.fit_transform(corpus)

    # ── data loading ──────────────────────────────────────────────
    def _load(self, csv_path: str, cache_path: str) -> None:
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as fh:
                self.rows = json.load(fh)
            return

        if not os.path.exists(csv_path):
            return

        # Collect English rows, then keep a fixed-stride deterministic sample.
        en_rows = []
        with open(csv_path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            for i, row in enumerate(csv.DictReader(fh)):
                if row.get("language") != "en":
                    continue
                en_rows.append(
                    {
                        "subject": _WS.sub(" ", row.get("subject", "")).strip(),
                        "body": _WS.sub(" ", row.get("body", "").replace("\\n", " "))[:400],
                        "queue": row.get("queue", ""),
                        "type": row.get("type", ""),
                        "priority": row.get("priority", ""),
                        "tags": [row.get(f"tag_{n}", "") for n in range(1, 9) if row.get(f"tag_{n}")],
                    }
                )

        rng = random.Random(42)  # deterministic
        if len(en_rows) > _MAX_SAMPLE:
            en_rows = rng.sample(en_rows, _MAX_SAMPLE)

        self.rows = en_rows
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as fh:
            json.dump(self.rows, fh, ensure_ascii=False)

    @property
    def size(self) -> int:
        return len(self.rows)

    # ── inference ─────────────────────────────────────────────────
    def similar_tickets(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Top-k most similar dataset tickets for *query* (any language —
        callers pass the bridged English query for hi/ta)."""
        if self.matrix is None or not query.strip():
            return []
        vec = self.vectorizer.transform([query])
        scores = cosine_similarity(vec, self.matrix).flatten()
        top = scores.argsort()[::-1][:k]
        results = []
        for idx in top:
            if scores[idx] <= 0:
                continue
            row = self.rows[int(idx)]
            results.append(
                {
                    "ref": f"DS-{idx + 1:05d}",
                    "subject": row["subject"],
                    "queue": row["queue"],
                    "type": row["type"],
                    "priority": row["priority"],
                    "score": round(float(scores[idx]), 4),
                }
            )
        return results

    def predict_signal(self, query: str, top_n: int = 5) -> Dict[str, Any]:
        """k-NN majority-vote queue prediction with match confidence."""
        sims = self.similar_tickets(query, k=top_n)
        if not sims:
            return {"queue": None, "confidence": 0.0, "basedOn": 0}
        votes: Dict[str, float] = {}
        for s in sims:
            votes[s["queue"]] = votes.get(s["queue"], 0.0) + s["score"]
        best = max(votes, key=votes.get)
        total = sum(votes.values()) or 1.0
        return {
            "queue": best,
            "confidence": round(votes[best] / total, 3),
            "basedOn": len(sims),
        }
