from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from models.news import NewsArticle
from models.company import Company
from services.news.news_pipeline import NewsPipeline
from core.config import settings

class NewsService:
    @staticmethod
    def refresh_company_news(db: Session, slug: str) -> Dict[str, Any]:
        company = db.query(Company).filter(Company.slug == slug, Company.is_deleted == False).first()
        if not company:
            raise ValueError(f"Company {slug} not found.")
            
        stats = NewsPipeline.process_company(db, company)
        return stats
        
    @staticmethod
    def get_company_news(db: Session, slug: str, limit: int = 10) -> List[NewsArticle]:
        company = db.query(Company).filter(Company.slug == slug, Company.is_deleted == False).first()
        if not company:
            raise ValueError(f"Company {slug} not found.")
            
        return db.query(NewsArticle).filter(NewsArticle.company_id == company.id).order_by(NewsArticle.published_at.desc()).limit(limit).all()
        
    @staticmethod
    def get_recent_news(db: Session, limit: int = 20) -> List[NewsArticle]:
        return db.query(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(limit).all()
        
    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        from models.news import NewsRunLog
        
        total_articles = db.query(NewsArticle).count()
        
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        articles_today = db.query(NewsArticle).filter(NewsArticle.retrieved_at >= today).count()
        
        week_ago = today - timedelta(days=7)
        articles_this_week = db.query(NewsArticle).filter(NewsArticle.retrieved_at >= week_ago).count()
        
        companies_with_news = db.query(NewsArticle.company_id).distinct().count()
        total_companies = db.query(Company).filter(Company.is_deleted == False).count()
        companies_without_news = total_companies - companies_with_news
        
        avg_articles_per_company = total_articles / companies_with_news if companies_with_news > 0 else 0
        
        avg_relevance = db.query(func.avg(NewsArticle.relevance_score)).scalar() or 0.0
        
        providers = db.query(NewsArticle.provider, func.count(NewsArticle.id)).group_by(NewsArticle.provider).all()
        provider_dist = {p[0]: p[1] for p in providers if p[0]}
        
        avg_refresh_duration = db.query(func.avg(NewsRunLog.duration_ms)).filter(NewsRunLog.duration_ms != None).scalar() or 0.0
        
        total_fetched = db.query(func.sum(NewsRunLog.articles_fetched)).scalar() or 0
        total_rejected = db.query(func.sum(NewsRunLog.articles_rejected)).scalar() or 0
        total_duplicates = db.query(func.sum(NewsRunLog.duplicates_removed)).scalar() or 0
        
        duplicate_percentage = (total_duplicates / total_fetched * 100) if total_fetched > 0 else 0.0
        rejected_percentage = (total_rejected / total_fetched * 100) if total_fetched > 0 else 0.0
        
        return {
            "total_articles": total_articles,
            "articles_today": articles_today,
            "articles_this_week": articles_this_week,
            "companies_with_news": companies_with_news,
            "companies_without_news": companies_without_news,
            "average_articles_per_company": float(avg_articles_per_company),
            "average_relevance_score": float(avg_relevance),
            "provider_distribution": provider_dist,
            "average_refresh_duration_ms": float(avg_refresh_duration),
            "duplicate_percentage": float(duplicate_percentage),
            "rejected_article_percentage": float(rejected_percentage)
        }
