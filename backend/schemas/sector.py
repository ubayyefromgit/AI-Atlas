from typing import List, Optional
from schemas.base import BaseSchema, BaseResponse

class SectorBase(BaseSchema):
    name: str
    definition: Optional[str] = None
    key_companies: List[str] = []
    primary_ai_entry_points: List[str] = []
    ai_adoption: Optional[str] = None
    market_size: Optional[str] = None
    regulatory_complexity: Optional[str] = None

class SectorResponse(SectorBase, BaseResponse):
    pass
