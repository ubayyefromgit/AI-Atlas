import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import random

from services.news.provider import NewsProvider

logger = logging.getLogger(__name__)

class MockNewsProvider(NewsProvider):
    """
    Returns mock news data for testing without hitting rate limits.
    """
    
    def fetch_news(self, company_name: str, website: Optional[str] = None) -> List[Dict[str, Any]]:
        logger.info(f"Generating mock news for {company_name}")
        
        now = datetime.now(timezone.utc)
        
        return [
            {
                "title": f"{company_name} announces breakthrough in AI-driven supply chain efficiency",
                "description": f"In a major announcement today, {company_name} revealed their new AI system that improves predictive maintenance and logistics by 40%.",
                "url": f"https://mock-news.com/article/{random.randint(1000, 9999)}",
                "published_at": now - timedelta(hours=random.randint(1, 48)),
                "source": "Tech Industry Daily"
            },
            {
                "title": f"Market analysis: {company_name}'s recent growth in the European sector",
                "description": f"Analysts predict strong Q3 results for {company_name} following their strategic expansion into the German and French food & beverage markets.",
                "url": f"https://mock-news.com/article/{random.randint(1000, 9999)}",
                "published_at": now - timedelta(hours=random.randint(48, 120)),
                "source": "Financial Tech Weekly"
            },
            {
                "title": f"New partnership formed between {company_name} and leading robotics firm",
                "description": f"The joint venture will focus on bringing cutting-edge automation to manufacturing floors, spearheaded by {company_name}.",
                "url": f"https://mock-news.com/article/{random.randint(1000, 9999)}",
                "published_at": now - timedelta(days=random.randint(5, 14)),
                "source": "Manufacturing Automation News"
            }
        ]
