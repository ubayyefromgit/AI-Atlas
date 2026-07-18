from typing import Optional
from sqlalchemy.orm import Session
from repositories.base import BaseRepository
from models.problem import Problem
from schemas.problem import ProblemBase

class ProblemRepository(BaseRepository[Problem, ProblemBase, ProblemBase]):
    def get_by_category(self, db: Session, *, category: str) -> Optional[Problem]:
        return db.query(Problem).filter(Problem.category == category, Problem.is_deleted == False).first()

problem_repo = ProblemRepository(Problem)
