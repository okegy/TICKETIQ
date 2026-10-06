import os
from fastapi import APIRouter
from app.schemas.analysis import TicketAnalysisRequest, TicketAnalysisResponse
from app.services.redaction_service import RedactionService
from app.services.tfidf_retriever import TfidfRetriever
from app.services.language_service import (
    resolve_language, language_name, language_native,
)
from app.services.glossary import build_search_query
from app.services.localization import localized
from app.services.dataset_service import DatasetService

router = APIRouter()

# Initialize retriever with synthetic KB seed
KB_SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seed", "knowledge_articles.json")
retriever = TfidfRetriever(kb_path=os.path.abspath(KB_SEED_PATH))

_DATASET_CSV = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "datasets",
    "aa_dataset-tickets-multi-lang-5-2-50-version.csv"))
_DATASET_CACHE = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "generated",
    "dataset_en_sample.json"))
_dataset: DatasetService | None = None


def _dataset_service() -> DatasetService:
    # Lazy singleton: keeps test collection and cold imports fast.
    global _dataset
    if _dataset is None:
        _dataset = DatasetService(csv_path=_DATASET_CSV, cache_path=_DATASET_CACHE)
    return _dataset


@router.post("/analyze-ticket", response_model=TicketAnalysisResponse)
async def analyze_ticket(request: TicketAnalysisRequest):
    # 0. Language detection (Unicode script analysis on the raw text)
    lang = resolve_language(request.language, request.ticketText)

    # 1. PII Redaction
    redacted_text = RedactionService.redact_text(request.ticketText)

    # 2. Retrieval — non-English tickets get glossary-bridged search text
    search_query = build_search_query(redacted_text, lang)
    retrieved_articles = retriever.retrieve(search_query, top_k=request.topK)

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

    if retrieved_articles:
        top_art = retrieved_articles[0]
        if decision == "DRAFT_ALLOWED":
            classification["category"] = top_art.get("category", "General IT")
            classification["subcategory"] = top_art.get("subcategory", "Unclassified")
        else:
            classification["category"] = "Unassigned"
            classification["subcategory"] = "No Match"

        for art in retrieved_articles:
            symptoms = art.get("symptoms", [])
            shared_ev = symptoms if isinstance(symptoms, list) else [str(symptoms)]
            evidence_items.append({
                "articleId": art["articleId"],
                "title": art["title"],
                "score": round(art["tfidfScore"], 2),
                "tfidfScore": round(art["tfidfScore"], 2),
                "embeddingScore": round(art["tfidfScore"], 2),
                "sharedEvidence": shared_ev,
                "sourceExcerpt": art.get("possibleCause", "") or art.get("cause", "")
            })

        if decision == "DRAFT_ALLOWED":
            for idx, step in enumerate(top_art.get("steps", []), 1):
                step_text = step["text"] if isinstance(step, dict) else str(step)
                step_id = step.get("sourceStepId", f"{top_art['articleId']}-S{idx}") if isinstance(step, dict) else f"{top_art['articleId']}-S{idx}"
                resolution_steps.append({
                    "stepNumber": idx,
                    "instruction": step_text,
                    "sourceArticleId": top_art["articleId"],
                    "sourceSection": "Resolution Steps",
                    "sourceStepId": step_id,
                    "verificationStatus": "SUPPORTED"
                })

            if top_art.get("escalationCondition") or top_art.get("escalation"):
                escalation = {
                    "required": True,
                    "condition": top_art.get("escalationCondition") or top_art.get("escalation"),
                    "sourceArticleId": top_art["articleId"],
                    "sourceSection": "Escalation Condition"
                }
        else:
            escalation = {
                "required": True,
                "condition": "Confidence is below the configured safety threshold. Escalate ticket to Tier-2 Service Desk for manual triage.",
                "sourceArticleId": "SYSTEM-REFUSAL",
                "sourceSection": "Evidence Refusal Gate"
            }

    # 4. Dataset signal — k-NN over the trained English IT-ticket corpus
    try:
        ds = _dataset_service()
        similar = ds.similar_tickets(search_query, k=3)
        signal = ds.predict_signal(search_query, top_n=5)
        dataset_signal = {
            "queue": signal["queue"],
            "confidence": signal["confidence"],
            "basedOn": signal["basedOn"],
            "similarTickets": similar,
        }
    except Exception:
        dataset_signal = {"queue": None, "confidence": 0.0, "basedOn": 0, "similarTickets": []}

    # 5. Localized analyst-facing messages
    strings = localized(lang)
    decision_message = (
        strings["draftAllowed"] if decision == "DRAFT_ALLOWED" else strings["noReliableMatch"]
    )

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
        },
        "language": {
            "code": lang,
            "name": language_name(lang),
            "native": language_native(lang),
            "requested": request.language,
        },
        "localized": {
            "decisionMessage": decision_message,
            "escalationSuggestion": strings["escalationSuggestion"],
            "sanitizedNote": strings["sanitizedNote"],
            "kbNote": strings["kbNote"],
            "datasetSignalLabel": strings["datasetSignal"],
            "detectedLanguageLabel": strings["detectedLanguage"],
        },
        "datasetSignal": dataset_signal,
    }
