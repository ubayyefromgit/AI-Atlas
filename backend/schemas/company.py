from typing import List, Optional, TypeVar, Generic, Dict
from pydantic import Field, HttpUrl
from schemas.base import BaseSchema, BaseResponse
from models.enums import CompanyStatus

T = TypeVar("T")

class FilterItem(BaseSchema):
    value: str
    count: int

class CompanyFilters(BaseSchema):
    ai_categories: List[FilterItem]
    segments: List[FilterItem]
    company_types: List[FilterItem]
    countries: List[FilterItem]
    maturity_levels: List[FilterItem]

class CompanyStatistics(BaseSchema):
    total_companies: int
    companies_per_segment: Dict[str, int]
    companies_per_ai_category: Dict[str, int]
    companies_per_company_type: Dict[str, int]
    maturity_distribution: Dict[str, int]
    country_distribution: Dict[str, int]
    problem_counts: Dict[str, int]
    average_maturity: float
    average_revenue: Optional[str] = None

class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    offset: int
    limit: int
    has_next: bool
    returned: int
    execution_ms: float

class CompanyBase(BaseSchema):
    name: str = Field(..., description="Unique company name", example="Krones AG")
    country: Optional[str] = Field(None, example="Germany")
    ai_category: Optional[str] = Field(None, example="Predictive Maintenance")
    segment_tags: List[str] = Field(default=[], example=["Packaging", "Bottling"])
    use_cases: List[str] = Field(default=[], example=["AI Quality Control"])
    top_german_customers: List[str] = Field(default=[])
    germany_presence: Optional[str] = None
    company_type: Optional[str] = Field(None, example="Enterprise")
    funding: Optional[str] = None
    estimated_revenue: Optional[str] = None
    maturity: Optional[int] = Field(None, ge=1, le=5, description="Maturity between 1-5", example=4)
    deployment_evidence: Optional[str] = None
    website: Optional[HttpUrl] = Field(None, example="https://www.krones.com")
    source: str = "dataset"
    status: CompanyStatus = CompanyStatus.APPROVED
    is_followed: bool = False

class CreateCompany(CompanyBase):
    pass

class UpdateCompany(BaseSchema):
    name: Optional[str] = None
    country: Optional[str] = None
    ai_category: Optional[str] = None
    segment_tags: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    top_german_customers: Optional[List[str]] = None
    germany_presence: Optional[str] = None
    company_type: Optional[str] = None
    funding: Optional[str] = None
    estimated_revenue: Optional[str] = None
    maturity: Optional[int] = Field(None, ge=1, le=5)
    deployment_evidence: Optional[str] = None
    website: Optional[HttpUrl] = None
    status: Optional[CompanyStatus] = None
    is_followed: Optional[bool] = None

class CompanyResponse(CompanyBase, BaseResponse):
    slug: str

class CompanySummary(BaseSchema):
    name: str = Field(..., example="Krones AG")
    slug: str = Field(..., example="krones-ag")
    ai_category: Optional[str] = Field(None, example="Predictive Maintenance")
    company_type: Optional[str] = Field(None, example="Enterprise")
    country: Optional[str] = Field(None, example="Germany")
    estimated_revenue: Optional[str] = None
    maturity: Optional[int] = Field(None, example=4)
    website: Optional[str] = Field(None, example="https://www.krones.com")
    is_followed: bool = False

class CompanyCard(CompanySummary):
    segment_tags: List[str] = Field(default=[], example=["Packaging", "Bottling"])

class ProblemSummary(BaseSchema):
    problem_name: str = Field(..., example="Supply Chain Delays")
    category: str = Field(..., example="Logistics")
    severity: Optional[str] = Field(None, example="High")
    roi_benchmark: Optional[str] = Field(None, example="15%")
    payback_period: Optional[str] = Field(None, example="12 months")
    affected_companies: Optional[str] = None
    financial_impact: Optional[str] = None
    regulatory_triggers: Optional[str] = None

class SearchSuggestion(BaseSchema):
    name: str = Field(..., example="Krones AG")
    slug: str = Field(..., example="krones-ag")
    segment: Optional[str] = Field(None, example="Packaging")
    score: float = Field(..., example=1.0)

class SummariesRequest(BaseSchema):
    slugs: List[str] = Field(..., example=["krones-ag", "khs-group"])
