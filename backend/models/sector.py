from sqlalchemy import Column, String, JSON
from core.database import Base
from models.base import BaseModelMixin

class Sector(Base, BaseModelMixin):
    __tablename__ = "sectors"

    name = Column(String, unique=True, index=True, nullable=False)
    definition = Column(String)
    
    # JSON array fields
    key_companies = Column(JSON, default=list)
    primary_ai_entry_points = Column(JSON, default=list)
    
    ai_adoption = Column(String)
    market_size = Column(String)
    regulatory_complexity = Column(String)
