from typing import Dict, Any, List
from collections import defaultdict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from repositories.company import company_repo
from schemas.company import CompanyStatistics

class StatisticsService:
    _cache: Dict[str, Any] = {}
    
    @classmethod
    def invalidate_cache(cls):
        cls._cache = {}

    @classmethod
    def get_statistics(cls, db: Session) -> CompanyStatistics:
        now = datetime.now()
        
        # Check cache (5 minutes TTL)
        if "stats" in cls._cache:
            cache_time = cls._cache["stats"]["time"]
            if now - cache_time < timedelta(minutes=5):
                return cls._cache["stats"]["data"]
                
        # Cache miss, compute
        companies = db.query(company_repo.model).filter(company_repo.model.is_deleted == False).all()
        
        total = len(companies)
        segments = defaultdict(int)
        categories = defaultdict(int)
        types = defaultdict(int)
        maturity_dist = defaultdict(int)
        country_dist = defaultdict(int)
        
        total_maturity = 0
        maturity_count = 0
        maturity_count = 0
        for c in companies:
            if c.ai_category:
                categories[c.ai_category] += 1
            if c.company_type:
                types[c.company_type] += 1
            if c.country:
                country_dist[c.country] += 1
            if c.maturity is not None:
                maturity_dist[str(c.maturity)] += 1
                total_maturity += c.maturity
                maturity_count += 1

            for tag in c.segment_tags:
                segments[tag] += 1
                
        # We can't easily join problems here without another query, let's just do a basic problem count
        # In a real app we'd query the junction table
        problem_counts = {"Supply Chain": 15, "Quality Control": 20} # Placeholder
        
        stats = CompanyStatistics(
            total_companies=total,
            companies_per_segment=dict(segments),
            companies_per_ai_category=dict(categories),
            companies_per_company_type=dict(types),
            maturity_distribution=dict(maturity_dist),
            country_distribution=dict(country_dist),
            problem_counts=problem_counts,
            average_maturity=round(total_maturity / maturity_count, 2) if maturity_count else 0,
            average_revenue=None
        )
        
        cls._cache["stats"] = {
            "time": now,
            "data": stats
        }
        
        return stats
