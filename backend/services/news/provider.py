import abc
from typing import List, Dict, Any, Optional

class NewsProvider(abc.ABC):
    """
    Abstract base class for all news providers.
    """
    @abc.abstractmethod
    def fetch_news(self, company_name: str, website: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch recent news articles for a company.
        
        Returns a list of dictionaries with at least the following keys:
        - title: str
        - description: str
        - url: str
        - published_at: datetime
        - source: str
        """
        pass

class NewsProviderFactory:
    """
    Factory to instantiate the configured news provider.
    """
    @staticmethod
    def get_provider(provider_name: str) -> NewsProvider:
        if provider_name.lower() == "gnews":
            from services.news.gnews_provider import GNewsProvider
            return GNewsProvider()
        elif provider_name.lower() == "googlerss":
            from services.news.google_rss_provider import GoogleRssProvider
            return GoogleRssProvider()
        elif provider_name.lower() == "mock":
            from services.news.mock_provider import MockNewsProvider
            return MockNewsProvider()
        else:
            raise ValueError(f"Unknown news provider: {provider_name}")
