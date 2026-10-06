from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.duplicate_service import DuplicateService
from app.services.knowledge_gap_service import KnowledgeGapService

router = APIRouter()

class DuplicateCheckRequest(BaseModel):
    ticketText: str
    historicalTickets: List[Dict[str, Any]]
    threshold: float = 0.65

class KnowledgeGapRequest(BaseModel):
    noMatchTickets: List[Dict[str, Any]]
    minClusterSize: int = 2

@router.post("/find-duplicates")
def find_duplicates(request: DuplicateCheckRequest):
    matches = DuplicateService.find_duplicates(
        current_ticket_text=request.ticketText,
        historical_tickets=request.historicalTickets,
        threshold=request.threshold
    )
    return {"duplicates": matches}

@router.post("/detect-knowledge-gaps")
def detect_knowledge_gaps(request: KnowledgeGapRequest):
    gaps = KnowledgeGapService.detect_knowledge_gaps(
        no_match_tickets=request.noMatchTickets,
        min_cluster_size=request.minClusterSize
    )
    return {"proposedTopics": gaps}
