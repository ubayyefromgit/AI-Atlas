import logging
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session

from core.config import settings
from models.company import Company
from models.news import NewsArticle
from services.news.provider import NewsProviderFactory
from services.news.relevance_filter import RelevanceFilter
from services.news.deduplicator import Deduplicator
from services.news.summarizer import Summarizer
from services.news.news_indexer import NewsIndexer

logger = logging.getLogger(__name__)

class NewsPipeline:
    """
    Orchestrates the fetching, filtering, deduplication, summarization, and indexing of news.
    """
    
    @staticmethod
    def process_company(db: Session, company: Company) -> Dict[str, Any]:
        """
        Runs the full news pipeline for a single company.
        Returns a dict of statistics for this run.
        """
        import time
        from models.news import NewsRunLog
        
        start_t = time.time()
        started_at = datetime.now(timezone.utc)
        
        stats = {
            "fetched": 0,
            "relevant": 0,
            "duplicates_removed": 0,
            "stored": 0,
            "indexed": 0
        }
        
        run_log = NewsRunLog(
            company_id=company.id,
            company_name=company.name,
            provider=settings.NEWS_PROVIDER,
            status="running",
            started_at=started_at
        )
        db.add(run_log)
        db.commit()
        db.refresh(run_log)
        
        try:
            # 1. Fetch
            provider = NewsProviderFactory.get_provider(settings.NEWS_PROVIDER)
            search_query = RelevanceFilter.clean_company_name(company.name)
            raw_articles = provider.fetch_news(search_query, company.website)
            stats["fetched"] = len(raw_articles)
            
            if raw_articles:
                # 2. Relevance Filter
                relevant_articles = []
                for article in raw_articles:
                    score = RelevanceFilter.calculate_score(article, company.name, company.website)
                    if score >= settings.NEWS_RELEVANCE_THRESHOLD:
                        article["relevance_score"] = score
                        relevant_articles.append(article)
                
                stats["relevant"] = len(relevant_articles)
                
                # 3. Deduplicate
                unique_articles = Deduplicator.filter_duplicates(db, company.id, relevant_articles)
                stats["duplicates_removed"] = len(relevant_articles) - len(unique_articles)
                
                # 4. Summarize and Store
                for article in unique_articles:
                    summary = Summarizer.summarize(article)
                    
                    db_article = NewsArticle(
                        company_id=company.id,
                        headline=article.get("title"),
                        summary=summary,
                        source=article.get("source"),
                        url=article.get("url"),
                        published_at=article.get("published_at"),
                        provider=settings.NEWS_PROVIDER,
                        retrieved_at=datetime.now(timezone.utc),
                        relevance_score=article.get("relevance_score")
                    )
                    
                    db.add(db_article)
                    try:
                        db.commit()
                        db.refresh(db_article)
                        stats["stored"] += 1
                        
                        # Generate notification if company is followed
                        if getattr(company, 'is_followed', False):
                            from models.notification import Notification, NotificationType
                            notif = Notification(
                                message=f"New news fetched for {company.name}: {db_article.headline}",
                                type=NotificationType.NEWS,
                                related_entity_id=company.id
                            )
                            db.add(notif)
                            db.commit()

                        # 5. Index
                        indexed = NewsIndexer.index_article(db, db_article, company)
                        if indexed:
                            stats["indexed"] += 1
                    except Exception as insert_e:
                        db.rollback()
                        logger.warning(f"Failed to insert article {article.get('url')} (likely a duplicate URL): {insert_e}")
                        
            # Update company refresh timestamp
            company.news_last_refreshed = datetime.now(timezone.utc)
            db.add(company)
            
            # Update Run Log
            run_log.status = "success" if stats["stored"] > 0 or stats["fetched"] == 0 else "partial_success"
            run_log.completed_at = datetime.now(timezone.utc)
            run_log.duration_ms = int((time.time() - start_t) * 1000)
            run_log.articles_fetched = stats["fetched"]
            run_log.articles_rejected = stats["fetched"] - stats["relevant"]
            run_log.duplicates_removed = stats["duplicates_removed"]
            run_log.articles_stored = stats["stored"]
            run_log.articles_indexed = stats["indexed"]
            
            db.add(run_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Pipeline error for company {company.name}: {e}")
            db.rollback()
            
            # Update Run Log on failure
            run_log.status = "failed"
            run_log.error_message = str(e)
            run_log.completed_at = datetime.now(timezone.utc)
            run_log.duration_ms = int((time.time() - start_t) * 1000)
            db.add(run_log)
            db.commit()
            raise
            
        return stats
