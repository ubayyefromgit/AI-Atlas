from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_
from slugify import slugify

from repositories.base import BaseRepository
from models.company import Company
from schemas.company import CreateCompany, UpdateCompany

class CompanyRepository(BaseRepository[Company, CreateCompany, UpdateCompany]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Company]:
        return db.query(Company).filter(Company.slug == slug, Company.is_deleted == False).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name == name, Company.is_deleted == False).first()

    def get_by_website(self, db: Session, *, website: str) -> Optional[Company]:
        return db.query(Company).filter(Company.website == website, Company.is_deleted == False).first()

    def generate_slug(self, db: Session, name: str) -> str:
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while db.query(Company).filter(Company.slug == slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def create(self, db: Session, *, obj_in: CreateCompany) -> Company:
        slug = self.generate_slug(db, obj_in.name)
        obj_in_data = obj_in.model_dump()
        if "website" in obj_in_data and obj_in_data["website"]:
            obj_in_data["website"] = str(obj_in_data["website"]) # HttpUrl to string
        
        db_obj = Company(**obj_in_data, slug=slug)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def update(self, db: Session, *, db_obj: Company, obj_in: UpdateCompany) -> Company:
        obj_data = obj_in.model_dump(exclude_unset=True)
        if "website" in obj_data and obj_data["website"]:
            obj_data["website"] = str(obj_data["website"])
            
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_filtered(
        self, db: Session, *, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        segment: Optional[str] = None,
        ai_category: Optional[str] = None,
        company_type: Optional[str] = None,
        maturity: Optional[int] = None,
        country: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        
        query = db.query(Company).filter(Company.is_deleted == False)

        if search:
            query = query.filter(or_(
                Company.name.ilike(f"%{search}%"),
                Company.country.ilike(f"%{search}%"),
                Company.ai_category.ilike(f"%{search}%")
            ))
            
        if segment:
            # Simple LIKE against JSON string representation works for small datasets without json_each
            query = query.filter(Company.segment_tags.ilike(f'%"{segment}"%'))
        
        if ai_category:
            query = query.filter(Company.ai_category == ai_category)
        if company_type:
            query = query.filter(Company.company_type == company_type)
        if maturity is not None:
            query = query.filter(Company.maturity == maturity)
        if country:
            query = query.filter(Company.country == country)
        if status:
            query = query.filter(Company.status == status.upper())

        # Sorting
        if sort_by and hasattr(Company, sort_by):
            column = getattr(Company, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            query = query.order_by(desc(Company.created_at))

        # We need to return both results and total count for pagination
        total = query.count()
        results = query.offset(skip).limit(limit).all()
        return results, total

    def get_problems(self, db: Session, slug: str) -> List[tuple]:
        from models.problem import Problem
        from models.mapping import ProblemCompanyMapping
        
        company = self.get_by_slug(db, slug=slug)
        if not company:
            return []
            
        results = (
            db.query(Problem, ProblemCompanyMapping)
            .join(ProblemCompanyMapping, Problem.id == ProblemCompanyMapping.problem_id)
            .filter(ProblemCompanyMapping.company_id == company.id)
            .all()
        )
        return results

    def get_summaries_by_slugs(self, db: Session, slugs: List[str]) -> List[Company]:
        return db.query(Company).filter(Company.slug.in_(slugs), Company.is_deleted == False).all()

company_repo = CompanyRepository(Company)
