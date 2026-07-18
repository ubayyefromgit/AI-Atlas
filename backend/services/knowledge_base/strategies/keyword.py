import re
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.kb_chunk import KBChunk
from models.enums import EmbeddingStatus
from services.knowledge_base.strategies.base import BaseRetrievalStrategy, RetrievalResult

class KeywordRetriever(BaseRetrievalStrategy):
    def retrieve(self, db: Session, query: str, limit: int = 10) -> List[RetrievalResult]:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        
        # Use production-ready stop words
        stop_words = ENGLISH_STOP_WORDS
        # Extract words longer than 2 characters
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        if not keywords:
            return []
            
        # Create an OR filter for all keywords
        filters = [KBChunk.content.ilike(f"%{w}%") for w in keywords]
        
        # Fetch ALL matching chunks (small DB, so safe)
        chunks = db.query(KBChunk).filter(
            KBChunk.embedding_status == EmbeddingStatus.INDEXED,
            or_(*filters)
        ).all()
        
        parsed = []
        for chunk in chunks:
            title = chunk.metadata_json.get("title", "")
            content_lower = chunk.content.lower()
            title_lower = title.lower()
            
            # Score based on how many keywords matched and where
            hit_count = sum(1 for w in keywords if w in content_lower)
            title_hit_count = sum(1 for w in keywords if w in title_lower)
            
            # Base score from content hits
            score = 0.5 + (0.1 * hit_count)
            # Bonus for title hits
            score += (0.2 * title_hit_count)
            
            # Cap at 1.0
            score = min(score, 1.0)
            
            parsed.append(RetrievalResult(
                chunk_key=chunk.chunk_key,
                source_type=chunk.source_type.value,
                source_id=chunk.source_id,
                title=title,
                content=chunk.content,
                score=score,
                matched_by="keyword",
                last_indexed=chunk.updated_at.isoformat() if chunk.updated_at else None
            ))
            
        # Sort by score descending and return limit
        parsed.sort(key=lambda x: x.score, reverse=True)
        return parsed[:limit]
