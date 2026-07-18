from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BaseResponse(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    # We do not expose is_deleted or deleted_at in the standard response
