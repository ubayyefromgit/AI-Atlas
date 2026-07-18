from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from core.database import Base
from models.base import BaseModelMixin

class ProblemCompanyMapping(Base, BaseModelMixin):
    __tablename__ = "problem_company_mappings"

    problem_id = Column(Integer, ForeignKey("problems.id"), index=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    
    segment = Column(String)
    vendor_rank = Column(Integer)
    roi_benchmark = Column(String)
    payback_period = Column(String)

    # Relationships
    problem = relationship("Problem", back_populates="company_mappings")
    company = relationship("Company", back_populates="problem_mappings")
