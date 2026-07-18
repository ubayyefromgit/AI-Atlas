from sqlalchemy import Column, String, Float, Integer, JSON, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from core.database import Base
from models.base import BaseModelMixin
from models.enums import CompanyStatus

class Company(Base, BaseModelMixin):
    __tablename__ = "companies"

    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    country = Column(String, index=True)
    ai_category = Column(String, index=True)
    
    # JSON array fields
    segment_tags = Column(JSON, default=list)
    use_cases = Column(JSON, default=list)
    top_german_customers = Column(JSON, default=list)
    
    germany_presence = Column(String)
    company_type = Column(String, index=True)
    
    funding = Column(String)
    estimated_revenue = Column(String)
    maturity = Column(Integer) # 1-5 scale
    deployment_evidence = Column(String)
    website = Column(String, unique=True)
    source = Column(String, default="dataset")
    status = Column(Enum(CompanyStatus), default=CompanyStatus.APPROVED)
    news_last_refreshed = Column(DateTime)
    is_followed = Column(Boolean, default=False)

    # Relationships
    news_articles = relationship("NewsArticle", back_populates="company")
    problem_mappings = relationship("ProblemCompanyMapping", back_populates="company")
