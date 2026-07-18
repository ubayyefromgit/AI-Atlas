from typing import Optional
from schemas.base import BaseSchema, BaseResponse

class ProblemBase(BaseSchema):
    category: str
    severity: Optional[str] = None
    ai_solution_use_case: Optional[str] = None
    affected_companies: Optional[str] = None
    financial_impact: Optional[str] = None
    regulatory_triggers: Optional[str] = None

class ProblemResponse(ProblemBase, BaseResponse):
    pass
