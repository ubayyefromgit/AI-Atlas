import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import timedelta

from models.news import NewsArticle

class Deduplicator:
    """
    Removes duplicate news articles.
    """
    
    @staticmethod
    def _normalize_title(title: str) -> str:
        # Remove punctuation, make lowercase, remove extra spaces
        t = re.sub(r'[^\w\s]', '', title.lower())
        return re.sub(r'\s+', ' ', t).strip()
        
    @staticmethod
    def filter_duplicates(db: Session, company_id: int, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not articles:
            return []
            
        # Get existing articles for this company in the DB (limit to recent to avoid massive loads)
        # Assuming we don't want to insert duplicates of any article we already have
        existing_db_articles = db.query(NewsArticle).filter(NewsArticle.company_id == company_id).all()
        existing_urls = {a.url for a in existing_db_articles if a.url}
        existing_norm_titles = {Deduplicator._normalize_title(a.headline) for a in existing_db_articles if a.headline}
        
        unique_articles = []
        seen_urls = set()
        seen_norm_titles = set()
        
        for article in articles:
            url = article.get("url")
            title = article.get("title", "")
            norm_title = Deduplicator._normalize_title(title)
            
            # Exact URL match (either in this batch or in DB)
            if url in seen_urls or url in existing_urls:
                continue
                
            # Normalized Title match (either in this batch or in DB)
            if norm_title in seen_norm_titles or norm_title in existing_norm_titles:
                continue
                
            unique_articles.append(article)
            seen_urls.add(url)
            seen_norm_titles.add(norm_title)
            
        return unique_articles
