from typing import List, Optional
import time
import logging
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.company import (
    CompanyResponse, CreateCompany, UpdateCompany, PaginatedResponse, 
    CompanySummary, CompanyCard, CompanyStatistics, CompanyFilters,
    SearchSuggestion, ProblemSummary, SummariesRequest
)
from services.company import CompanyService
from services.statistics import StatisticsService
from services.filters import FilterService
from services.search import SearchService

router = APIRouter()

# Setup API Logger
api_logger = logging.getLogger("api")
api_logger.setLevel(logging.INFO)

def create_paginated_response(results: List, total: int, skip: int, limit: int, execution_ms: float):
    return {
        "items": results,
        "total": total,
        "offset": skip,
        "limit": limit,
        "has_next": (skip + limit) < total,
        "returned": len(results),
        "execution_ms": execution_ms
    }

@router.get("/", response_model=PaginatedResponse[CompanyResponse])
def get_companies(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None, segment: Optional[str] = None,
    ai_category: Optional[str] = None, company_type: Optional[str] = None,
    maturity: Optional[int] = Query(None, ge=1, le=5), country: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = None, sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    start = time.time()
    results, total = CompanyService.get_companies(
        db, skip, limit, search, segment, ai_category, company_type, maturity, country, status, sort_by, sort_order
    )
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies | latency={exec_ms}ms | status=200")
    return create_paginated_response(results, total, skip, limit, exec_ms)

@router.get("/cards", response_model=PaginatedResponse[CompanyCard])
def get_company_cards(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None, segment: Optional[str] = None,
    ai_category: Optional[str] = None, company_type: Optional[str] = None,
    maturity: Optional[int] = Query(None, ge=1, le=5), country: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = None, sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    start = time.time()
    results, total = CompanyService.get_companies(
        db, skip, limit, search, segment, ai_category, company_type, maturity, country, status, sort_by, sort_order
    )
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/cards | latency={exec_ms}ms | status=200")
    return create_paginated_response(results, total, skip, limit, exec_ms)

@router.get("/search", response_model=List[SearchSuggestion])
def search_companies(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    start = time.time()
    res = SearchService.search_autocomplete(db, q, limit)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/search?q={q} | latency={exec_ms}ms | status=200")
    return res

@router.get("/statistics", response_model=CompanyStatistics)
def get_statistics(db: Session = Depends(get_db)):
    start = time.time()
    res = StatisticsService.get_statistics(db)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/statistics | latency={exec_ms}ms | status=200")
    return res

@router.get("/filters", response_model=CompanyFilters)
def get_filters(db: Session = Depends(get_db)):
    start = time.time()
    res = FilterService.get_filters(db)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/filters | latency={exec_ms}ms | status=200")
    return res

@router.post("/summaries", response_model=List[CompanySummary])
def get_summaries_by_slugs(req: SummariesRequest, db: Session = Depends(get_db)):
    start = time.time()
    res = CompanyService.get_summaries_by_slugs(db, req.slugs)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"POST /companies/summaries | latency={exec_ms}ms | status=200")
    return res

@router.get("/discover/quick")
def quick_discover_company(name: str = Query(..., min_length=2)):
    start = time.time()
    from services.discovery.quick_discovery import QuickDiscoveryService
    service = QuickDiscoveryService()
    res = service.discover_company(name)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/discover/quick?name={name} | latency={exec_ms}ms | status=200")
    
    if not res:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Company not found via web search")
        
    return res

@router.get("/{slug}", response_model=CompanyResponse)
def get_company_by_slug(slug: str, db: Session = Depends(get_db)):
    start = time.time()
    res = CompanyService.get_company(db, slug=slug)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/{slug} | latency={exec_ms}ms | status=200")
    return res

@router.get("/{slug}/summary", response_model=CompanySummary)
def get_company_summary(slug: str, db: Session = Depends(get_db)):
    start = time.time()
    res = CompanyService.get_company(db, slug=slug)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/{slug}/summary | latency={exec_ms}ms | status=200")
    return res

@router.get("/{slug}/problems", response_model=List[ProblemSummary])
def get_company_problems(slug: str, db: Session = Depends(get_db)):
    start = time.time()
    res = CompanyService.get_company_problems(db, slug=slug)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"GET /companies/{slug}/problems | latency={exec_ms}ms | status=200")
    return res

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(company_in: CreateCompany, db: Session = Depends(get_db)):
    return CompanyService.create_company(db, obj_in=company_in)

@router.put("/{slug}", response_model=CompanyResponse)
def update_company(slug: str, company_in: UpdateCompany, db: Session = Depends(get_db)):
    return CompanyService.update_company(db, slug=slug, obj_in=company_in)

@router.delete("/{slug}", response_model=CompanyResponse)
def delete_company(slug: str, db: Session = Depends(get_db)):
    return CompanyService.delete_company(db, slug=slug)

@router.post("/{slug}/follow", response_model=CompanyResponse)
def follow_company(slug: str, db: Session = Depends(get_db)):
    start = time.time()
    company = CompanyService.get_company(db, slug=slug)
    company.is_followed = True
    db.commit()
    db.refresh(company)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"POST /companies/{slug}/follow | latency={exec_ms}ms | status=200")
    return company

@router.post("/{slug}/unfollow", response_model=CompanyResponse)
def unfollow_company(slug: str, db: Session = Depends(get_db)):
    start = time.time()
    company = CompanyService.get_company(db, slug=slug)
    company.is_followed = False
    db.commit()
    db.refresh(company)
    exec_ms = round((time.time() - start) * 1000, 2)
    api_logger.info(f"POST /companies/{slug}/unfollow | latency={exec_ms}ms | status=200")
    return company
