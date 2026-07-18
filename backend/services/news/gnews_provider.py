import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import urllib.parse

from core.config import settings
from services.news.provider import NewsProvider

logger = logging.getLogger(__name__)

class GNewsProvider(NewsProvider):
    """
    Fetches news from the official GNews REST API (gnews.io).
    """
    BASE_URL = "https://gnews.io/api/v4/search"
    
    def fetch_news(self, company_name: str, website: Optional[str] = None) -> List[Dict[str, Any]]:
        if not settings.NEWS_API_KEY:
            logger.warning("NEWS_API_KEY is not configured.")
            return []
            
        # Build query. Using company name. Optionally could add website domain logic to query if needed,
        # but usually it's best to filter after fetching to ensure we get broad enough results.
        # "COMPANY_NAME" ensures exact phrase match
        q = f'"{company_name}"'
        
        params = {
            "q": q,
            "lang": "en",
            "max": settings.NEWS_MAX_RESULTS,
            "apikey": settings.NEWS_API_KEY,
            "sortby": "publishedAt"
        }
        
        try:
            with httpx.Client(timeout=settings.NEWS_TIMEOUT) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                articles = data.get("articles", [])
                results = []
                
                for article in articles:
                    # GNews returns publishedAt as ISO string "2023-01-01T12:00:00Z"
                    try:
                        pub_at = datetime.fromisoformat(article.get("publishedAt", "").replace("Z", "+00:00"))
                    except ValueError:
                        pub_at = datetime.now(timezone.utc)
                        
                    results.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "published_at": pub_at,
                        "source": article.get("source", {}).get("name", "Unknown")
                    })
                    
                return results
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("GNews API rate limit exceeded.")
            else:
                logger.error(f"GNews API HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch news from GNews: {e}")
            raise
