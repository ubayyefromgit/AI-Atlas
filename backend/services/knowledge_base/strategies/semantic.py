from typing import List
from sqlalchemy.orm import Session
from services.knowledge_base.strategies.base import BaseRetrievalStrategy, RetrievalResult
from services.knowledge_base.embeddings import embedding_service
from services.knowledge_base.vector_store import vector_store

class SemanticRetriever(BaseRetrievalStrategy):
    def retrieve(self, db: Session, query: str, limit: int = 10) -> List[RetrievalResult]:
        query_embedding = embedding_service.get_embedding(query)
        results = vector_store.search(query_embedding, limit=limit)
        
        parsed = []
        for r in results:
            meta = r['metadata']
            parsed.append(RetrievalResult(
                chunk_key=meta.get("chunk_key", r['id']),
                source_type=meta.get("source_type", "unknown"),
                source_id=str(meta.get("source_id", "")),
                title=meta.get("title", ""),
                content=r['document'],
                score=r['score'],
                matched_by="semantic"
            ))
        return parsed
