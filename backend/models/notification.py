from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Integer, ForeignKey
from datetime import datetime, timezone
from core.database import Base
from models.base import BaseModelMixin
import enum

class NotificationType(str, enum.Enum):
    NEWS = "NEWS"
    SYSTEM = "SYSTEM"

class Notification(Base, BaseModelMixin):
    __tablename__ = "notifications"
    
    message = Column(String, nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Optional relation to a company or other entity
    related_entity_id = Column(Integer, nullable=True)
