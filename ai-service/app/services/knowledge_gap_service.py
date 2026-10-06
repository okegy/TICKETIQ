from typing import List, Dict, Any
from collections import Counter
import re

class KnowledgeGapService:
    @staticmethod
    def detect_knowledge_gaps(no_match_tickets: List[Dict[str, Any]], min_cluster_size: int = 2) -> List[Dict[str, Any]]:
        """
        Analyze tickets that resulted in NO_RELIABLE_MATCH to identify recurring keywords/patterns
        and recommend new Knowledge Base article topics.
        """
        if not no_match_tickets:
            return []

        stopwords = {"the", "and", "is", "in", "to", "of", "a", "for", "with", "on", "at", "from", "by", "this", "that", "it", "an"}
        word_ticket_map = {}

        for ticket in no_match_tickets:
            text = (ticket.get("description", "") or ticket.get("ticketText", "")).lower()
            words = set(re.findall(r'\b[a-zA-Z]{4,}\b', text)) - stopwords
            t_id = ticket.get("ticketId") or ticket.get("id", "UNKNOWN")
            for w in words:
                if w not in word_ticket_map:
                    word_ticket_map[w] = []
                word_ticket_map[w].append(t_id)

        # Find words appearing in multiple tickets
        recurring = {w: tids for w, tids in word_ticket_map.items() if len(tids) >= min_cluster_size}

        clusters = []
        for word, tids in recurring.items():
            clusters.append({
                "proposedTopic": f"Troubleshooting recurring {word.capitalize()} issues",
                "patternKeyword": word,
                "affectedTicketCount": len(tids),
                "affectedTicketIds": tids,
                "recommendation": f"Multiple unmatched incidents mention '{word}'. Recommend creating an approved KB standard operating procedure."
            })

        clusters.sort(key=lambda x: x["affectedTicketCount"], reverse=True)
        return clusters[:5]
