from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models.kb_chunk import KBChunk
from models.enums import EmbeddingStatus, SourceType
from services.knowledge_base.vector_store import vector_store
from services.knowledge_base.strategies.hybrid import HybridRetriever
from services.knowledge_base.reranker import Reranker
from services.knowledge_base.strategies.base import RetrievalResult

logger = logging.getLogger("ingestion")

class KnowledgeBaseService:
    def __init__(self):
        self.retriever = HybridRetriever()

    def upsert_chunk(
        self, 
        db: Session,
        source_type: SourceType,
        source_id: str,
        chunk_key: str,
        content: str,
        document_hash: str,
        embedding: List[float],
        metadata_json: Dict[str, Any]
    ) -> KBChunk:
        """Central method to safely put things in ChromaDB and sync SQLite"""
        
        # 1. Store in Chroma
        vector_store.upsert(
            id=chunk_key,
            embedding=embedding,
            document=content,
            metadata=metadata_json
        )
        
        # 2. Store in SQLite metadata tracker
        existing = db.query(KBChunk).filter(KBChunk.chunk_key == chunk_key).first()
        if existing:
            existing.content = content
            existing.document_hash = document_hash
            existing.metadata_json = metadata_json
            existing.embedding_status = EmbeddingStatus.INDEXED
            existing.updated_at = datetime.utcnow()
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            new_chunk = KBChunk(
                source_type=source_type,
                source_id=source_id,
                chunk_key=chunk_key,
                document_hash=document_hash,
                content=content,
                metadata_json=metadata_json,
                embedding_status=EmbeddingStatus.INDEXED
            )
            db.add(new_chunk)
            db.commit()
            db.refresh(new_chunk)
            return new_chunk

    def delete_chunk(self, db: Session, chunk_key: str):
        # Remove from Chroma
        try:
            vector_store.delete(chunk_key)
        except Exception as e:
            logger.warning(f"Error deleting from chroma: {e}")
            
        # Remove from SQLite
        existing = db.query(KBChunk).filter(KBChunk.chunk_key == chunk_key).first()
        if existing:
            existing.is_deleted = True
            db.add(existing)
            db.commit()
            
    def search(self, db: Session, query: str, limit: int = 10) -> List[RetrievalResult]:
        # 1. Strategy execution (Hybrid merges Semantic + Keyword)
        results = self.retriever.retrieve(db, query, limit=limit * 2) # Fetch extra for reranking
        
        # 2. Rerank
        reranked = Reranker.rerank(query, results)
        
        return reranked[:limit]

kb_service = KnowledgeBaseService()
