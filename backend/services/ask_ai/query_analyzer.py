from typing import Dict, Any

class QueryAnalyzer:
    """
    Analyzes the user's question to determine intent and extract keywords.
    Helps optimize the retrieval query against the Knowledge Base.
    """
    
    def analyze(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        
        # 1. Comparison Intent
        is_comparison = any(word in question_lower for word in [
            "compare", "difference", "vs", "versus", "better", "worse", "instead of"
        ])
        
        # 2. News Intent
        is_news = any(word in question_lower for word in [
            "recent", "news", "lately", "latest", "update", "announce"
        ])
        
        # 3. Entity type detection heuristics (very basic string matching)
        is_company = any(word in question_lower for word in [
            "company", "gmbh", "ag", "startup", "corporation"
        ])
        
        is_sector = any(word in question_lower for word in [
            "sector", "industry", "market"
        ])
        
        is_problem = any(word in question_lower for word in [
            "problem", "challenge", "issue", "difficulty", "solve", "solution"
        ])
        
        # 4. General search intent
        is_general = not (is_comparison or is_news or is_company or is_sector or is_problem)
        
        # 5. Expand very short queries to improve vector retrieval quality.
        # Acronyms or single company names don't embed well without context words.
        optimized_query = question
        words = question.strip().split()
        if len(words) <= 2 and len(question.strip()) <= 20:
            # Likely a company name or acronym — add retrieval context
            optimized_query = f"{question} AI company technology platform solutions"
        
        return {
            "is_comparison": is_comparison,
            "is_news": is_news,
            "is_company": is_company,
            "is_sector": is_sector,
            "is_problem": is_problem,
            "is_general": is_general,
            "optimized_query": optimized_query
        }
