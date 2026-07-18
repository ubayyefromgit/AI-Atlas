from typing import List
from sqlalchemy.orm import Session
from repositories.company import company_repo
from schemas.company import SearchSuggestion

class SearchService:
    @staticmethod
    def search_autocomplete(db: Session, query: str, limit: int = 10) -> List[SearchSuggestion]:
        query_lower = query.lower()
        companies = db.query(company_repo.model).filter(company_repo.model.is_deleted == False).all()
        
        results = []
        for c in companies:
            score = 0.0
            name_lower = c.name.lower()
            
            # Exact match
            if name_lower == query_lower:
                score += 10.0
            # Starts with
            elif name_lower.startswith(query_lower):
                score += 5.0
            # Contains
            elif query_lower in name_lower:
                score += 2.0
                
            # Category match
            if c.ai_category and query_lower in c.ai_category.lower():
                score += 1.0
                
            # Segment match
            for tag in c.segment_tags:
                if query_lower in tag.lower():
                    score += 1.5
                    break
                    
            if score > 0:
                results.append({
                    "c": c,
                    "score": score
                })
                
        # Sort by score desc, then name asc
        results.sort(key=lambda x: (-x["score"], x["c"].name))
        
        # Take top limit
        top = results[:limit]
        
        suggestions = []
        for r in top:
            c = r["c"]
            segment = c.segment_tags[0] if c.segment_tags else None
            suggestions.append(
                SearchSuggestion(
                    name=c.name,
                    slug=c.slug,
                    segment=segment,
                    score=r["score"]
                )
            )
            
        return suggestions
