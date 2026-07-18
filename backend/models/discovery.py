from sqlalchemy import Column, String, Float, Integer, JSON, Enum, DateTime
from core.database import Base
from models.base import BaseModelMixin
from models.enums import DiscoveryStatus

class DiscoveryCandidate(Base, BaseModelMixin):
    __tablename__ = "discovery_candidates"

    name = Column(String, index=True, nullable=False)
    country = Column(String, index=True)
    ai_category = Column(String, index=True)
    
    segment_tags = Column(JSON, default=list)
    use_cases = Column(JSON, default=list)
    
    website = Column(String, unique=True, index=True)
    
    # Store evidence items [{url, title, snippet, retrieved_at}]
    evidence = Column(JSON, default=list)
    
    # Confidence breakdown
    confidence_score = Column(Float, nullable=False, default=0.0)
    confidence_explanation = Column(JSON, default=dict)
    
    validation_result = Column(JSON, default=dict)
    
    status = Column(Enum(DiscoveryStatus), default=DiscoveryStatus.PENDING)

class DiscoveryRunLog(Base, BaseModelMixin):
    __tablename__ = "discovery_run_logs"
    
    sector = Column(String, nullable=False)
    country = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    status = Column(String, nullable=False) # e.g., success, failed
    
    candidates_retrieved = Column(Integer, default=0)
    candidates_approved = Column(Integer, default=0)
    candidates_rejected = Column(Integer, default=0)
    
    error_message = Column(String, nullable=True)
