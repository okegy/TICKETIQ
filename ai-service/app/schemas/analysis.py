from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TicketAnalysisRequest(BaseModel):
    ticketId: str
    ticketText: str
    structuredFields: Optional[Dict[str, Any]] = None
    topK: int = 3
    confidenceThreshold: float = 0.62
    retrievalMode: str = "hybrid"

class ExtractedFields(BaseModel):
    application: Optional[str] = None
    errorCode: Optional[str] = None
    affectedUsers: Optional[int] = None
    trigger: Optional[str] = None

class Classification(BaseModel):
    category: str
    subcategory: str
    confidence: float
    alternatives: List[Dict[str, Any]] = []

class EvidenceItem(BaseModel):
    articleId: str
    title: str
    score: float
    tfidfScore: float
    embeddingScore: float
    sharedEvidence: List[str]
    sourceExcerpt: str

class ConfidenceMetrics(BaseModel):
    finalScore: float
    retrievalRelevance: float
    ticketCompleteness: float
    sourceAgreement: float
    groundingCoverage: float
    rationale: List[str]

class ResolutionStep(BaseModel):
    stepNumber: int
    instruction: str
    sourceArticleId: str
    sourceSection: str
    sourceStepId: str
    verificationStatus: str = "SUPPORTED"

class Escalation(BaseModel):
    required: bool
    condition: Optional[str] = None
    sourceArticleId: Optional[str] = None
    sourceSection: Optional[str] = None

class AnalysisConfiguration(BaseModel):
    retrievalMode: str
    threshold: float
    promptVersion: str

class TicketAnalysisResponse(BaseModel):
    decision: str
    redactedText: str
    extractedFields: ExtractedFields
    missingFields: List[str]
    classification: Classification
    evidence: List[EvidenceItem]
    confidence: ConfidenceMetrics
    resolutionSteps: List[ResolutionStep]
    escalation: Escalation
    possibleDuplicates: List[str] = []
    configuration: AnalysisConfiguration
