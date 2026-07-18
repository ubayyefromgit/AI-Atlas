from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from core.database import Base
from models.base import BaseModelMixin

class NewsArticle(Base, BaseModelMixin):
    __tablename__ = "news_articles"

    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    headline = Column(String, nullable=False)
    summary = Column(String)
    source = Column(String)
    url = Column(String, unique=True)
    published_at = Column(DateTime, index=True)
    provider = Column(String)
    retrieved_at = Column(DateTime)
    relevance_score = Column(Float)

    # Relationships
    company = relationship("Company", back_populates="news_articles")

class NewsRunLog(Base, BaseModelMixin):
    __tablename__ = "news_run_logs"

    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=True)
    company_name = Column(String)
    provider = Column(String)
    status = Column(String, nullable=False) # 'success', 'partial_success', 'failed'
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)
    error_message = Column(String, nullable=True)
    
    articles_fetched = Column(Integer, default=0)
    articles_rejected = Column(Integer, default=0)
    duplicates_removed = Column(Integer, default=0)
    articles_stored = Column(Integer, default=0)
    articles_indexed = Column(Integer, default=0)

    # Relationships
    company = relationship("Company")
