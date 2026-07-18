from datetime import datetime
from typing import Optional, Dict
from pydantic import HttpUrl, BaseModel
from schemas.base import BaseSchema, BaseResponse

class NewsBase(BaseSchema):
    company_id: int
    headline: str
    summary: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None # Using string instead of HttpUrl to avoid strict validation errors on weird domains
    published_at: Optional[datetime] = None
    provider: Optional[str] = None
    retrieved_at: Optional[datetime] = None
    relevance_score: Optional[float] = None

class NewsResponse(NewsBase, BaseResponse):
    pass

class NewsStatisticsResponse(BaseSchema):
    total_articles: int
    articles_today: int
    articles_this_week: int
    companies_with_news: int
    companies_without_news: int
    average_articles_per_company: float
    average_relevance_score: float
    provider_distribution: Dict[str, int]
    average_refresh_duration_ms: float
    duplicate_percentage: float
    rejected_article_percentage: float
    
class NewsHealthResponse(BaseSchema):
    provider_status: str
    scheduler_status: str
    last_refresh_time: Optional[datetime]
    last_failure: Optional[str]
    pending_jobs: int
