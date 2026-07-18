# backend/services/ingestion/validators.py
import logging
from pydantic import ValidationError
from typing import Dict, Any, Tuple, Optional
from schemas.company import CreateCompany
from schemas.problem import ProblemBase
from schemas.sector import SectorBase

logger = logging.getLogger("ingestion")

class RowValidationError(Exception):
    pass

def validate_company(row_data: Dict[str, Any]) -> Tuple[Optional[CreateCompany], list[str]]:
    warnings = []
    if not row_data.get("name"):
        return None, ["Missing required field: name"]
        
    try:
        company = CreateCompany(**row_data)
        return company, warnings
    except ValidationError as e:
        err_msgs = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return None, err_msgs

def validate_problem(row_data: Dict[str, Any]) -> Tuple[Optional[ProblemBase], list[str]]:
    warnings = []
    if not row_data.get("category"):
        return None, ["Missing required field: category"]
        
    try:
        problem = ProblemBase(**row_data)
        return problem, warnings
    except ValidationError as e:
        err_msgs = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return None, err_msgs

def validate_sector(row_data: Dict[str, Any]) -> Tuple[Optional[SectorBase], list[str]]:
    warnings = []
    if not row_data.get("name"):
        return None, ["Missing required field: name"]
        
    try:
        sector = SectorBase(**row_data)
        return sector, warnings
    except ValidationError as e:
        err_msgs = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return None, err_msgs
