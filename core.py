import os
import re
import json
import pathlib
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RedactionService:
    @staticmethod
    def redact_text(text: str) -> str:
        if not text:
            return ""

        # 1. Email Redaction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        redacted = re.sub(email_pattern, '[REDACTED_EMAIL]', text)

        # 2. IP Address Redaction (IPv4)
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        redacted = re.sub(ip_pattern, '[REDACTED_IP]', redacted)

        # 3. Phone Number Redaction
        phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        redacted = re.sub(phone_pattern, '[REDACTED_PHONE]', redacted)
        redacted = re.sub(r'\b\d{3}[-.\s]\d{4}\b', '[REDACTED_PHONE]', redacted)

        # 4. Bearer Tokens & API Keys
        token_pattern = r'(?i)(bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*|api[_-]?key[:=]\s*[a-zA-Z0-9_\-]+)'
        redacted = re.sub(token_pattern, '[REDACTED_TOKEN]', redacted)

        # 5. Passwords in text (e.g. password: Test@12345 or password is XYZ)
        password_pattern = r'(?i)(password|passwd|pwd)\s*[:=]\s*\S+'
        redacted = re.sub(password_pattern, r'\1: [REDACTED_SECRET]', redacted)

        # 6. URLs & internal hostnames
        url_pattern = r'https?://[^\s]+'
        redacted = re.sub(url_pattern, '[REDACTED_URL]', redacted)

        return redacted

class Assistant:
    def __init__(self, kb_path: str = None, threshold: float = 0.15):
        self.threshold = threshold
        if kb_path is None:
            # Look in multiple candidate locations
            candidates = [
                pathlib.Path(__file__).parent.parent / "ticketiq-verification-kit" / "samples" / "articles_sample.json",
                pathlib.Path(__file__).parent / "data" / "seed" / "articles_sample.json",
                pathlib.Path(__file__).parent / "data" / "seed" / "knowledge_articles.json"
            ]
            for c in candidates:
                if c.exists():
                    kb_path = str(c)
                    break

        if not kb_path or not os.path.exists(kb_path):
            raise FileNotFoundError(f"Knowledge base file not found at {kb_path}")

        self.kb_path = kb_path
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            self.articles: List[Dict[str, Any]] = json.load(f)

        self.vectorizer = TfidfVectorizer(stop_words='english')
        corpus = []
        for art in self.articles:
            symptoms = art.get("symptoms", "")
            if isinstance(symptoms, list):
                symptoms = " ".join(symptoms)
            cause = art.get("cause", "") or art.get("possibleCause", "")
            steps = art.get("steps", [])
            if isinstance(steps, list):
                steps_str = " ".join([s if isinstance(s, str) else s.get("text", "") for s in steps])
            else:
                steps_str = str(steps)
            corpus.append(f"{art.get('title', '')} {art.get('category', '')} {art.get('subcategory', '')} {symptoms} {cause} {steps_str}")

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def analyze(self, description: str, error_text: str = "") -> Dict[str, Any]:
        # Handle empty/whitespace input
        if not description or not description.strip():
            raise ValueError("Validation Error: Ticket description cannot be empty or whitespace only.")

        # 1. Normalize and redact text
        combined_raw = f"{description} {error_text}".strip()
        clean_text = RedactionService.redact_text(description.strip())
        clean_combined = RedactionService.redact_text(combined_raw)

        # 2. Retrieve top-3 articles
        query_vec = self.vectorizer.transform([clean_combined])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:3]

        articles_result = []
        for idx in top_indices:
            art = self.articles[idx]
            art_id = art.get("id") or art.get("articleId", f"KB-{idx+1:02d}")
            score_val = round(float(scores[idx]), 4)
            articles_result.append({
                "id": art_id,
                "title": art.get("title", "Untitled Article"),
                "score": score_val,
                "category": art.get("category", "General IT"),
                "subcategory": art.get("subcategory", "General"),
                "steps": art.get("steps", []),
                "escalation": art.get("escalation") or art.get("escalationCondition", "")
            })

        # Sort descending by score
        articles_result.sort(key=lambda x: -x["score"])

        top_art = articles_result[0]
        top_score = top_art["score"]

        # Decision Gate (O5)
        matched = top_score >= self.threshold

        if matched:
            category = top_art["category"]
            subcategory = top_art["subcategory"]
            confidence = top_score

            # Grounded draft citing article id (O4)
            steps = top_art.get("steps", [])
            steps_lines = []
            for i, st in enumerate(steps, 1):
                step_text = st if isinstance(st, str) else st.get("text", "")
                steps_lines.append(f"{i}. [{top_art['id']}] {step_text}")
            
            draft = (
                f"Resolution Draft grounded in [{top_art['id']}] - {top_art['title']}:\n"
                f"Category: {category} / Subcategory: {subcategory}\n"
                f"Steps:\n" + "\n".join(steps_lines) + "\n"
                f"Escalation Rule: {top_art.get('escalation', 'Escalate if unresolved after following steps.')}"
            )
        else:
            category = "Unassigned"
            subcategory = "No Match"
            confidence = top_score
            draft = (
                f"No reliable match found in knowledge base (confidence {confidence:.2f} is below safety threshold {self.threshold:.2f}). "
                f"Recommended escalation: Suggest routing ticket to specialized Tier-2 Support for triage. No resolution steps generated."
            )

        # Articles output format: {id, title, score}
        formatted_articles = [
            {"id": a["id"], "title": a["title"], "score": a["score"]}
            for a in articles_result
        ]

        return {
            "matched": matched,
            "category": category,
            "subcategory": subcategory,
            "confidence": confidence,
            "articles": formatted_articles,
            "draft": draft,
            "clean_text": clean_text
        }
