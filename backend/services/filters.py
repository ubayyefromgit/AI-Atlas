from typing import List, Dict, Any
from collections import defaultdict
from sqlalchemy.orm import Session

from repositories.company import company_repo
from schemas.company import CompanyFilters, FilterItem

class FilterService:
    @staticmethod
    def get_filters(db: Session) -> CompanyFilters:
        """
        Extracts dynamic filters from the dataset via application-side processing.
        Normalizes, deduplicates, and sorts alphabetically.
        """
        companies = db.query(company_repo.model).filter(company_repo.model.is_deleted == False).all()
        
        categories = defaultdict(int)
        segments = defaultdict(int)
        types = defaultdict(int)
        countries = defaultdict(int)
        maturities = defaultdict(int)
        
        for c in companies:
            if c.ai_category:
                categories[c.ai_category] += 1
            if c.company_type:
                types[c.company_type] += 1
            if c.country:
                countries[c.country] += 1
            if c.maturity is not None:
                maturities[str(c.maturity)] += 1
                
            for tag in c.segment_tags:
                segments[tag] += 1
                
        def format_filter(d: Dict[str, int]) -> List[FilterItem]:
            return [FilterItem(value=k, count=v) for k, v in sorted(d.items())]
            
        return CompanyFilters(
            ai_categories=format_filter(categories),
            segments=format_filter(segments),
            company_types=format_filter(types),
            countries=format_filter(countries),
            maturity_levels=format_filter(maturities)
        )
