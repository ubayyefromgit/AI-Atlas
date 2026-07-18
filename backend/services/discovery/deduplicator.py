import re
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from models.company import Company
from models.discovery import DiscoveryCandidate

class Deduplicator:
    def check_duplicate(self, db: Session, name: str, website: str) -> bool:
        """
        Checks if a company with similar name or domain already exists 
        in either Company or DiscoveryCandidate.
        Returns True if it is a duplicate.
        """
        norm_name = self._normalize_name(name)
        domain = self._extract_domain(website)
        
        # Check Company table
        companies = db.query(Company).all()
        for c in companies:
            if self._extract_domain(c.website) == domain:
                return True
            if self._normalize_name(c.name) == norm_name:
                return True
                
        # Check DiscoveryCandidate table (excluding rejected)
        candidates = db.query(DiscoveryCandidate).filter(DiscoveryCandidate.status != "rejected").all()
        for c in candidates:
            if self._extract_domain(c.website) == domain:
                return True
            if self._normalize_name(c.name) == norm_name:
                return True
                
        return False
        
    def _normalize_name(self, name: str) -> str:
        if not name:
            return ""
        name = name.lower()
        # Remove common suffixes
        name = re.sub(r'\b(inc|llc|ltd|corp|ag|gmbh|co)\b\.?', '', name)
        # Remove non-alphanumeric
        name = re.sub(r'[^a-z0-9]', '', name)
        return name
        
    def _extract_domain(self, url: str) -> str:
        if not url:
            return ""
        if not url.startswith("http"):
            url = "http://" + url
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return url.lower()
