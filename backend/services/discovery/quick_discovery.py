import logging
from typing import Dict, Any, Optional

from services.discovery.provider_factory import DiscoveryProviderFactory
from services.discovery.extractor import Extractor

logger = logging.getLogger(__name__)

def _clean_company_dict(comp: Dict[str, Any], company_name: str) -> Dict[str, Any]:
    """Sanitize and normalize a raw extracted company dict before returning."""
    # Ensure required fields exist with sensible defaults
    name = comp.get("name") or company_name
    website = comp.get("website") or ""
    
    # Strip trailing slash from website to avoid validation issues
    if isinstance(website, str):
        website = website.rstrip("/")

    return {
        "name": name,
        "country": comp.get("country"),
        "ai_category": comp.get("ai_category"),
        "segment_tags": comp.get("segment_tags") or [],
        "use_cases": comp.get("use_cases") or [],
        "website": website if website else None,
        "source": "web_discovery",
        "status": "approved",
    }


class QuickDiscoveryService:
    def __init__(self):
        self.provider = DiscoveryProviderFactory.get_provider()
        self.extractor = Extractor()

    def discover_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        On-the-fly discovery for a specific company name.
        Searches the web, extracts via LLM, returns a clean dict (not saved to DB).
        """
        query = f"{company_name} AI company"
        logger.info(f"Quick discovery search: {query}")

        try:
            results = self.provider.search(query, max_results=5)
            if not results:
                logger.warning(f"No web results for '{company_name}'")
                return None

            extracted = self.extractor.extract(
                sector="Technology", country="Global", evidence=results
            )

            if not extracted:
                logger.warning(f"LLM returned no companies for '{company_name}'")
                return None

            # 1. Try exact name match first
            for comp in extracted:
                if company_name.lower() in comp.get("name", "").lower():
                    return _clean_company_dict(comp, company_name)

            # 2. Fallback: best match is the first extracted company
            return _clean_company_dict(extracted[0], company_name)

        except Exception as e:
            logger.error(f"Quick discovery failed for '{company_name}': {e}", exc_info=True)
            return None
