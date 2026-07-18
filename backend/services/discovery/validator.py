import httpx
from typing import Dict, Any, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class Validator:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def validate(self, candidate: Dict[str, Any]) -> Tuple[bool, list, bool]:
        """
        Validates the candidate data and website.
        Returns: (is_valid, reasons, website_verified)
        """
        reasons = []
        is_valid = True
        website_verified = False

        # Basic schema checks
        required_fields = ["name", "country", "website"]
        for field in required_fields:
            if not candidate.get(field):
                is_valid = False
                reasons.append(f"Missing required field: {field}")

        if not candidate.get("evidence_urls"):
            is_valid = False
            reasons.append("No evidence URLs associated")

        website_url = candidate.get("website")
        if website_url:
            # Website verification
            verified, reason = self._verify_website(website_url, candidate.get("name", ""))
            website_verified = verified
            if not verified:
                # We do not strictly invalidate based on website failing because of anti-bot protections,
                # but we will note it and it affects confidence score.
                reasons.append(f"Website verification failed: {reason}")
            else:
                reasons.append("Website verified successfully")
        
        return is_valid, reasons, website_verified

    def _verify_website(self, url: str, name: str) -> Tuple[bool, str]:
        if not url.startswith("http"):
            url = f"https://{url}"
            
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                
                # Check title similarity
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                
                # Simple check: Does the title contain words from the name?
                if name and title:
                    name_words = set(name.lower().split())
                    title_words = set(title.lower().split())
                    if name_words.intersection(title_words) or name.lower() in title.lower():
                        return True, "Title matches name"
                    else:
                        return True, f"Site responded but title '{title}' may not match '{name}'"
                
                return True, "Site responded (no title check possible)"
                
        except Exception as e:
            return False, str(e)
