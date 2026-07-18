from services.discovery.provider import DiscoveryProvider
from services.discovery.tavily_provider import TavilyProvider
from core.config import settings

class DiscoveryProviderFactory:
    @staticmethod
    def get_provider() -> DiscoveryProvider:
        provider_name = settings.DISCOVERY_PROVIDER.lower()
        if provider_name == "tavily":
            return TavilyProvider()
        # Add Google Custom Search, Bing, etc. here in the future
        else:
            return TavilyProvider() # Fallback
