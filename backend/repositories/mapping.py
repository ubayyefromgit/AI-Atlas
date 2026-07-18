from typing import Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from models.mapping import ProblemCompanyMapping
from pydantic import BaseModel

# Quick create schema for mappings (internal)
class CreateMapping(BaseModel):
    company_id: int
    problem_id: int
    segment: Optional[str] = None
    roi_benchmark: Optional[str] = None

class MappingRepository(BaseRepository[ProblemCompanyMapping, CreateMapping, CreateMapping]):
    def get_by_unique_keys(self, db: Session, *, company_id: int, problem_id: int, segment: Optional[str]) -> Optional[ProblemCompanyMapping]:
        return db.query(ProblemCompanyMapping).filter(
            ProblemCompanyMapping.company_id == company_id,
            ProblemCompanyMapping.problem_id == problem_id,
            ProblemCompanyMapping.segment == segment,
            ProblemCompanyMapping.is_deleted == False
        ).first()

mapping_repo = MappingRepository(ProblemCompanyMapping)
