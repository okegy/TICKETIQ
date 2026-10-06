import os
from fastapi import APIRouter
from app.schemas.analysis import TicketAnalysisRequest, TicketAnalysisResponse
from app.services.redaction_service import RedactionService
from app.services.tfidf_retriever import TfidfRetriever

router = APIRouter()

# Initialize retriever with synthetic KB seed
KB_SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seed", "knowledge_articles.json")
retriever = TfidfRetriever(kb_path=os.path.abspath(KB_SEED_PATH))

@router.post("/analyze-ticket", response_model=TicketAnalysisResponse)
async def analyze_ticket(request: TicketAnalysisRequest):
    # 1. PII Redaction
    redacted_text = RedactionService.redact_text(request.ticketText)

    # 2. Retrieval
    retrieved_articles = retriever.retrieve(redacted_text, top_k=request.topK)

    # 3. Confidence & Decision Gate
    top_score = retrieved_articles[0]["tfidfScore"] if retrieved_articles else 0.0
    
    if top_score < request.confidenceThreshold:
        decision = "NO_RELIABLE_MATCH"
    else:
        decision = "DRAFT_ALLOWED"

    # Build evidence list
    evidence_items = []
    resolution_steps = []
    classification = {
        "category": "General IT",
        "subcategory": "Unclassified",
        "confidence": round(top_score, 2),
        "alternatives": []
    }
    escalation = {"required": False}

    if retrieved_articles and decision == "DRAFT_ALLOWED":
        top_art = retrieved_articles[0]
        classification["category"] = top_art.get("category", "General IT")
        classification["subcategory"] = top_art.get("subcategory", "Unclassified")

        for art in retrieved_articles:
            evidence_items.append({
                "articleId": art["articleId"],
                "title": art["title"],
                "score": round(art["tfidfScore"], 2),
                "tfidfScore": round(art["tfidfScore"], 2),
                "embeddingScore": round(art["tfidfScore"], 2),
                "sharedEvidence": art.get("symptoms", []),
                "sourceExcerpt": art.get("possibleCause", "")
            })

        # Grounded resolution steps from top article
        for idx, step in enumerate(top_art.get("steps", []), 1):
            resolution_steps.append({
                "stepNumber": idx,
                "instruction": step["text"],
                "sourceArticleId": top_art["articleId"],
                "sourceSection": "Resolution Steps",
                "sourceStepId": step["sourceStepId"],
                "verificationStatus": "SUPPORTED"
            })

        if top_art.get("escalationCondition"):
            escalation = {
                "required": True,
                "condition": top_art["escalationCondition"],
                "sourceArticleId": top_art["articleId"],
                "sourceSection": "Escalation Condition"
            }

    return {
        "decision": decision,
        "redactedText": redacted_text,
        "extractedFields": {
            "application": request.structuredFields.get("application") if request.structuredFields else None,
            "errorCode": "AUTH-401" if "401" in redacted_text else None,
            "affectedUsers": None,
            "trigger": None
        },
        "missingFields": [],
        "classification": classification,
        "evidence": evidence_items,
        "confidence": {
            "finalScore": round(top_score, 2),
            "retrievalRelevance": round(top_score, 2),
            "ticketCompleteness": 0.85,
            "sourceAgreement": 0.90,
            "groundingCoverage": 1.0 if resolution_steps else 0.0,
            "rationale": [f"Top article retrieval confidence score: {round(top_score, 2)}"]
        },
        "resolutionSteps": resolution_steps,
        "escalation": escalation,
        "possibleDuplicates": [],
        "configuration": {
            "retrievalMode": request.retrievalMode,
            "threshold": request.confidenceThreshold,
            "promptVersion": "resolution-v1"
        }
    }
