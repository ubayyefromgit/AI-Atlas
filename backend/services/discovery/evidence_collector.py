from typing import List
from schemas.discovery import EvidenceItem
from services.discovery.provider_factory import DiscoveryProviderFactory
import logging

logger = logging.getLogger(__name__)

class EvidenceCollector:
    def __init__(self):
        self.provider = DiscoveryProviderFactory.get_provider()

    def collect(self, sector: str, country: str, max_results_per_query: int = 10) -> List[EvidenceItem]:
        queries = [
            f"AI companies {sector} {country}",
            f"{sector} automation companies {country}",
            f"machine vision companies {sector} {country}",
            f"industrial AI companies {sector} {country}"
        ]
        
        all_evidence: List[EvidenceItem] = []
        seen_urls = set()
        
        for query in queries:
            logger.info(f"Running discovery query: {query}")
            results = self.provider.search(query, max_results=max_results_per_query)
            for item in results:
                # Normalize URL for deduplication (strip trailing slash)
                norm_url = item.url.strip().rstrip('/')
                if norm_url not in seen_urls:
                    seen_urls.add(norm_url)
                    all_evidence.append(item)
                    
        return all_evidence
