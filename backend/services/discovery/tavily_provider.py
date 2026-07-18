import httpx
from typing import List
from datetime import datetime, timezone
from core.config import settings
from schemas.discovery import EvidenceItem
from services.discovery.provider import DiscoveryProvider
import logging

logger = logging.getLogger(__name__)

class TavilyProvider(DiscoveryProvider):
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"

    def search(self, query: str, max_results: int = 10) -> List[EvidenceItem]:
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not configured. Mocking search for dev.")
            return self._mock_search(query)
            
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_domains": [],
            "exclude_domains": [],
            "max_results": max_results,
            "include_images": False,
        }
        
        try:
            with httpx.Client(timeout=settings.DISCOVERY_TIMEOUT) as client:
                response = client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    results.append(EvidenceItem(
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        snippet=item.get("content", ""),
                        retrieved_at=datetime.now(timezone.utc).isoformat()
                    ))
                return results
                
        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {e}")
            return []

    def _mock_search(self, query: str) -> List[EvidenceItem]:
        return [
            EvidenceItem(
                url="https://example-ai.com",
                title=f"Example AI Company matching '{query}'",
                snippet="We build intelligent automated solutions for this industry.",
                retrieved_at=datetime.now(timezone.utc).isoformat()
            )
        ]
