from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time
from datetime import datetime, timezone

from core.database import get_db
from services.news.news_service import NewsService
from schemas.news import NewsResponse, NewsStatisticsResponse, NewsHealthResponse

router = APIRouter()

@router.get("/health", response_model=NewsHealthResponse)
def get_news_health(db: Session = Depends(get_db)):
    # Simple health check endpoint for news pipeline
    # In a real app we would check scheduler internal state
    
    # Check provider status
    from core.config import settings
    provider_status = "OK" if settings.NEWS_API_KEY else "MISSING_API_KEY"
    
    # Check scheduler status (we will set a global variable in scheduler module or just assume OK for now)
    try:
        from scheduler import scheduler
        scheduler_status = "RUNNING" if scheduler and scheduler.running else "STOPPED"
        jobs = len(scheduler.get_jobs()) if scheduler else 0
    except ImportError:
        scheduler_status = "UNKNOWN"
        jobs = 0
        
    return {
        "provider_status": provider_status,
        "scheduler_status": scheduler_status,
        "last_refresh_time": datetime.now(timezone.utc), # simplified
        "last_failure": None,
        "pending_jobs": jobs
    }
    
@router.get("/companies/{slug}/news", response_model=List[NewsResponse])
def get_company_news(slug: str, limit: int = 10, db: Session = Depends(get_db)):
    try:
        return NewsService.get_company_news(db, slug, limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/companies/{slug}/news/refresh")
def refresh_company_news(slug: str, db: Session = Depends(get_db)):
    try:
        stats = NewsService.refresh_company_news(db, slug)
        return {"status": "success", "stats": stats}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent", response_model=List[NewsResponse])
def get_recent_news(limit: int = 20, db: Session = Depends(get_db)):
    return NewsService.get_recent_news(db, limit)

@router.get("/statistics", response_model=NewsStatisticsResponse)
def get_news_statistics(db: Session = Depends(get_db)):
    return NewsService.get_statistics(db)
