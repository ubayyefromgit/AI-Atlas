from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

class EvidenceItem(BaseModel):
    url: str
    title: str
    snippet: str
    retrieved_at: str

class ConfidenceExplanation(BaseModel):
    website_verified: bool = False
    evidence_count: int = 0
    field_completeness: float = 0.0
    duplicate_penalty: float = 0.0
    final_confidence: float = 0.0

class ValidationResult(BaseModel):
    is_valid: bool = False
    reasons: List[str] = []

class DiscoveryRequest(BaseModel):
    sector: str
    country: str

class DiscoveryCandidateBase(BaseModel):
    name: str
    country: Optional[str] = None
    ai_category: Optional[str] = None
    segment_tags: List[str] = []
    use_cases: List[str] = []
    website: Optional[str] = None

class DiscoveryCandidateResponse(DiscoveryCandidateBase):
    id: int
    evidence: List[EvidenceItem]
    confidence_score: float
    confidence_explanation: ConfidenceExplanation
    validation_result: ValidationResult
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DiscoveryStatisticsResponse(BaseModel):
    discovery_runs: int
    pending_candidates: int
    approved_candidates: int
    rejected_candidates: int
    average_confidence: float
    average_runtime_ms: float
    duplicate_percentage: float
    website_verification_success_rate: float
    average_evidence_count: float
    average_verification_time_ms: float
    average_extraction_time_ms: float
