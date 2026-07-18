from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories.company import company_repo
from schemas.company import CreateCompany, UpdateCompany
from models.company import Company
from services.statistics import StatisticsService

class CompanyService:
    @staticmethod
    def create_company(db: Session, obj_in: CreateCompany) -> Company:
        if company_repo.get_by_name(db, name=obj_in.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company with this name already exists.")
        if obj_in.website and company_repo.get_by_website(db, website=str(obj_in.website)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company with this website already exists.")

        company = company_repo.create(db, obj_in=obj_in)
        
        # Index into Knowledge Base immediately
        from services.knowledge_base.indexer import KnowledgeBaseIndexer
        try:
            indexer = KnowledgeBaseIndexer(db)
            indexer.index_company(company)
        except Exception as e:
            # Non-blocking, but ideally logged
            pass
            
        StatisticsService.invalidate_cache()
        return company

    @staticmethod
    def get_company(db: Session, slug: str) -> Company:
        company = company_repo.get_by_slug(db, slug=slug)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
        return company

    @staticmethod
    def get_companies(
        db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None, segment: Optional[str] = None,
        ai_category: Optional[str] = None, company_type: Optional[str] = None, maturity: Optional[int] = None,
        country: Optional[str] = None, status: Optional[str] = None, sort_by: Optional[str] = None, sort_order: str = "asc"
    ) -> Tuple[List[Company], int]:
        return company_repo.get_filtered(
            db, skip=skip, limit=limit, search=search, segment=segment, ai_category=ai_category, 
            company_type=company_type, maturity=maturity, country=country, status=status, sort_by=sort_by, sort_order=sort_order
        )

    @staticmethod
    def update_company(db: Session, slug: str, obj_in: UpdateCompany) -> Company:
        company = company_repo.get_by_slug(db, slug=slug)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
            
        if obj_in.name and obj_in.name != company.name:
            if company_repo.get_by_name(db, name=obj_in.name):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company with this name already exists.")
        if obj_in.website and str(obj_in.website) != company.website:
            if company_repo.get_by_website(db, website=str(obj_in.website)):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company with this website already exists.")

        updated = company_repo.update(db, db_obj=company, obj_in=obj_in)
        
        # Re-index into Knowledge Base immediately
        from services.knowledge_base.indexer import KnowledgeBaseIndexer
        try:
            indexer = KnowledgeBaseIndexer(db)
            indexer.index_company(updated)
        except Exception as e:
            pass
            
        StatisticsService.invalidate_cache()
        return updated

    @staticmethod
    def delete_company(db: Session, slug: str) -> Company:
        company = company_repo.get_by_slug(db, slug=slug)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
        deleted = company_repo.remove(db, id=company.id)
        StatisticsService.invalidate_cache()
        return deleted
        
    @staticmethod
    def get_company_problems(db: Session, slug: str) -> List[dict]:
        results = company_repo.get_problems(db, slug)
        problems = []
        for prob, mapping in results:
            problems.append({
                "problem_name": prob.ai_solution_use_case or prob.category or "Unknown Problem",
                "category": prob.category or "Unknown",
                "severity": prob.severity,
                "roi_benchmark": mapping.roi_benchmark,
                "payback_period": mapping.payback_period,
                "affected_companies": prob.affected_companies,
                "financial_impact": prob.financial_impact,
                "regulatory_triggers": prob.regulatory_triggers
            })
        return problems
        
    @staticmethod
    def get_summaries_by_slugs(db: Session, slugs: List[str]) -> List[Company]:
        return company_repo.get_summaries_by_slugs(db, slugs)
