import logging
import httpx
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import urllib.parse

from services.news.provider import NewsProvider

logger = logging.getLogger(__name__)

class GoogleRssProvider(NewsProvider):
    """
    Fetches news from the official (but undocumented) Google News RSS endpoint.
    It is 100% free and has no strict rate limits.
    """
    BASE_URL = "https://news.google.com/rss/search"
    
    def fetch_news(self, company_name: str, website: Optional[str] = None) -> List[Dict[str, Any]]:
        # httpx automatically url-encodes params, so we don't need to quote the company name
        q = company_name
        
        params = {
            "q": q,
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en"
        }
        
        try:
            # Google RSS returns XML
            with httpx.Client(timeout=15.0) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                results = []
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    description = item.find('description').text if item.find('description') is not None else ""
                    source_element = item.find('source')
                    source = source_element.text if source_element is not None else "Google News"
                    
                    try:
                        pub_at = parsedate_to_datetime(pubDate)
                    except Exception:
                        pub_at = datetime.now(timezone.utc)
                        
                    results.append({
                        "title": title,
                        "description": description,
                        "url": link,
                        "published_at": pub_at,
                        "source": source
                    })
                    
                return results
                
        except Exception as e:
            logger.error(f"Failed to fetch news from Google RSS: {e}")
            raise
