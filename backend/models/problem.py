from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from core.database import Base
from models.base import BaseModelMixin

class Problem(Base, BaseModelMixin):
    __tablename__ = "problems"

    category = Column(String, index=True, nullable=False)
    severity = Column(String)
    ai_solution_use_case = Column(String)
    affected_companies = Column(String)
    financial_impact = Column(String)
    regulatory_triggers = Column(String)

    # Relationships
    company_mappings = relationship("ProblemCompanyMapping", back_populates="problem")
