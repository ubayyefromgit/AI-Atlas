from sqlalchemy import Column, String, Text, Integer, JSON, Enum
from core.database import Base
from models.base import BaseModelMixin
from models.enums import SourceType, EmbeddingStatus

class KBChunk(Base, BaseModelMixin):
    __tablename__ = "kb_chunks"

    source_type = Column(Enum(SourceType), index=True, nullable=False)
    source_id = Column(String, index=True, nullable=False)
    chunk_key = Column(String, unique=True, index=True, nullable=False)
    document_hash = Column(String, nullable=True)
    
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    
    embedding_provider = Column(String, nullable=True)
    embedding_dimension = Column(Integer, nullable=True)
    embedding_status = Column(Enum(EmbeddingStatus), default=EmbeddingStatus.PENDING)
