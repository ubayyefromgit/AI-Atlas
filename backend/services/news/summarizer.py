import logging
from typing import Dict, Any

from bs4 import BeautifulSoup
from services.ask_ai.llm.factory import LLMFactory

logger = logging.getLogger(__name__)

class Summarizer:
    """
    Summarizes news articles.
    """
    
    @staticmethod
    def summarize(article: Dict[str, Any]) -> str:
        title = article.get("title", "")
        raw_desc = article.get("description", "")
        
        # Strip HTML tags from description
        desc = ""
        if raw_desc:
            try:
                soup = BeautifulSoup(raw_desc, "html.parser")
                desc = soup.get_text(separator=" ", strip=True)
            except Exception:
                desc = raw_desc
        
        try:
            llm = LLMFactory.get_client()
            system_prompt = "You are a professional business news summarizer."
            user_prompt = f"""
            Summarize the following news article in a concise manner (MAXIMUM 120 words).
            Focus on the key business facts.
            
            Title: {title}
            Description: {desc}
            """
            
            response = llm.generate_response(system_prompt, user_prompt, temperature=0.2, max_retries=1)
            
            if response and len(response.strip()) > 10:
                return response.strip()
            
        except Exception as e:
            logger.warning(f"Summarizer failed: {e}. Falling back to original description.")
            
        # Fallback
        return desc if desc else title
