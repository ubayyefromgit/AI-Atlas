from typing import List
from services.knowledge_base.strategies.base import RetrievalResult

class Reranker:
    @staticmethod
    def rerank(query: str, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Lightweight custom reranker.
        Promotes exact name matches (e.g. exact company or problem name).
        """
        query_lower = query.lower().strip()
        
        for r in results:
            title_lower = r.title.lower().strip()
            
            # Massive boost for exact title match
            if query_lower == title_lower:
                r.score += 2.0
            # Moderate boost for starts with (e.g. searching "Krones" matches "Krones AG")
            elif title_lower.startswith(query_lower):
                r.score += 1.0
            # Minor boost if query is in the title anywhere
            elif query_lower in title_lower:
                r.score += 0.5
                
        # Re-sort after reranking
        results.sort(key=lambda x: x.score, reverse=True)
        return results
