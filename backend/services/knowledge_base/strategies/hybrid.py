from typing import List
from sqlalchemy.orm import Session

from services.knowledge_base.strategies.base import BaseRetrievalStrategy, RetrievalResult
from services.knowledge_base.strategies.semantic import SemanticRetriever
from services.knowledge_base.strategies.keyword import KeywordRetriever

class HybridRetriever(BaseRetrievalStrategy):
    def __init__(self):
        self.semantic = SemanticRetriever()
        self.keyword = KeywordRetriever()
        
    def retrieve(self, db: Session, query: str, limit: int = 10) -> List[RetrievalResult]:
        sem_results = self.semantic.retrieve(db, query, limit=limit)
        kw_results = self.keyword.retrieve(db, query, limit=limit)
        
        # Merge and deduplicate, preferring semantic score if both exist, but combining matched_by
        # Weighted scoring: 0.7 semantic + 0.3 keyword if both
        merged_map = {}
        
        for r in sem_results:
            merged_map[r.chunk_key] = r
            
        for r in kw_results:
            if r.chunk_key in merged_map:
                existing = merged_map[r.chunk_key]
                existing.matched_by = "hybrid"
                # Boost the score significantly if matched by both
                existing.score = max(existing.score, r.score) + 0.2
            else:
                # Apply a penalty to pure keyword results to prefer semantic in hybrid
                r.score = r.score * 0.5 
                merged_map[r.chunk_key] = r
                
        # Sort by hybrid score
        final_list = list(merged_map.values())
        final_list.sort(key=lambda x: x.score, reverse=True)
        return final_list[:limit]
