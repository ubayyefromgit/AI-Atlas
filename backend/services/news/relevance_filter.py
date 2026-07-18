import logging
import urllib.parse
from typing import Optional, Dict, Any

from core.config import settings
from services.ask_ai.llm.factory import LLMFactory

logger = logging.getLogger(__name__)

class RelevanceFilter:
    """
    Filters news articles based on relevance to the company.
    Computes a float score 0.0 - 1.0.
    """
    
    @staticmethod
    def clean_company_name(company_name: str) -> str:
        import re
        core_name = re.sub(r'\([^)]*\)', '', company_name.lower())
        core_name = re.sub(r'\b(inc|llc|ltd|ag|gmbh|corp|corporation|nv|plc|sa|se|ai|technologies|solutions|group|holdings|division|systems)\b\.?', '', core_name).strip()
        core_name = core_name.split(' ai for ')[0].strip()
        return core_name

    @staticmethod
    def calculate_score(article: Dict[str, Any], company_name: str, website: Optional[str] = None) -> float:
        title = article.get("title", "").lower()
        desc = article.get("description", "").lower()
        url = article.get("url", "").lower()
        
        company_name_lower = company_name.lower()
        core_name = RelevanceFilter.clean_company_name(company_name_lower)
        
        score = 0.0
        
        # 1. Company name in title
        if company_name_lower in title or (core_name and core_name in title):
            score += 0.5
            
        # 2. Company name in description
        if company_name_lower in desc or (core_name and core_name in desc):
            score += 0.3
            
        # 3. Domain match
        if website:
            try:
                domain = urllib.parse.urlparse(website).netloc.lower()
                domain = domain.replace("www.", "")
                if domain and (domain in url or domain in desc):
                    score += 0.2
            except Exception:
                pass
                
        # Cap score at 1.0
        score = min(score, 1.0)
        
        # 4. Uncertain range? Ask Gemini
        if 0.4 <= score < 0.8: # Adjusted upper bound to catch partial matches without domain
            score = RelevanceFilter._ask_gemini_verification(article, company_name, score)
            
        return score
        
    @staticmethod
    def _ask_gemini_verification(article: Dict[str, Any], company_name: str, current_score: float) -> float:
        try:
            llm = LLMFactory.get_client()
            
            system_prompt = "You are a helpful data validator. You respond ONLY with 'YES' or 'NO'."
            user_prompt = f"""
            Is the following news article primarily about the company '{company_name}'?
            
            Title: {article.get('title')}
            Description: {article.get('description')}
            
            Respond only with YES or NO.
            """
            
            response = llm.generate_response(system_prompt, user_prompt, temperature=0.0)
            
            if "YES" in response.upper():
                logger.info(f"Gemini verified relevance for '{article.get('title')}'")
                return 0.9 # Verified
            else:
                logger.info(f"Gemini rejected relevance for '{article.get('title')}'")
                return 0.1 # Rejected
                
        except Exception as e:
            logger.warning(f"Failed to verify relevance with Gemini: {e}. Falling back to heuristic score.")
            return current_score
