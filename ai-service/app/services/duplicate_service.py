from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class DuplicateService:
    @staticmethod
    def find_duplicates(current_ticket_text: str, historical_tickets: List[Dict[str, Any]], threshold: float = 0.65) -> List[Dict[str, Any]]:
        """
        Compare current ticket description against historical tickets to identify potential duplicates.
        """
        if not historical_tickets or not current_ticket_text:
            return []

        descriptions = [t.get("description", "") or t.get("rawDescription", "") for t in historical_tickets]
        all_texts = [current_ticket_text] + descriptions

        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_mat = vectorizer.fit_transform(all_texts)
        except Exception:
            return []

        # Cosine similarity of first item with the rest
        sims = cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:]).flatten()

        matches = []
        for idx, score in enumerate(sims):
            if score >= threshold:
                ticket = historical_tickets[idx]
                matches.append({
                    "ticketId": ticket.get("ticketId") or ticket.get("id"),
                    "title": ticket.get("title", "Untitled"),
                    "similarityScore": round(float(score), 2),
                    "status": ticket.get("status", "RESOLVED")
                })

        matches.sort(key=lambda x: x["similarityScore"], reverse=True)
        return matches[:3]
