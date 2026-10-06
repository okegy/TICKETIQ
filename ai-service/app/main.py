import os

def _load_env_file(path: str) -> None:
    """Minimal .env loader; real environment variables always win."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

_load_env_file(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import analysis, knowledge, chat, batch

_evaluation_service = None  # lazy singleton (EvaluationService)
from app.utils.priority_rules import evaluate_priority
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="TicketIQ AI Service",
    description="AI Service for IT Support Resolution Copilot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/ai", tags=["analysis"])
app.include_router(knowledge.router, prefix="/ai", tags=["knowledge"])
app.include_router(chat.router, prefix="/ai", tags=["chat"])
app.include_router(batch.router, prefix="/ai", tags=["batch"])

class PriorityRequest(BaseModel):
    ticketText: str
    category: Optional[str] = ""
    subcategory: Optional[str] = ""

@app.post("/ai/priority", tags=["analysis"])
def get_priority(req: PriorityRequest):
    """Evaluate deterministic priority/urgency rules for a ticket description."""
    return evaluate_priority(req.ticketText, req.category or "", req.subcategory or "")

@app.get("/ai/languages", tags=["analysis"])
def list_languages():
    """Supported interface languages for the multilingual analyst UI."""
    from app.services.language_service import SUPPORTED_LANGUAGES
    return {
        "default": "en",
        "languages": [
            {"code": code, "name": meta["name"], "native": meta["native"]}
            for code, meta in SUPPORTED_LANGUAGES.items()
        ],
    }

@app.get("/ai/evaluate-thresholds", tags=["analysis"])
def evaluate_thresholds():
    """Real threshold sweep over the labeled evaluation set — measured coverage,
    refusal accuracy, and false refusals at every candidate threshold."""
    global _evaluation_service
    if _evaluation_service is None:
        from app.services.evaluation_service import EvaluationService
        _evaluation_service = EvaluationService()
    return _evaluation_service.sweep()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "TicketIQ AI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
