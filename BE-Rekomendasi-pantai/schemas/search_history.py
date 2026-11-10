from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SearchHistoryCreate(BaseModel):
    keyword: str = Field(min_length=1, max_length=500)
    result_count: int = Field(default=0, ge=0)


class SearchHistoryResponse(BaseModel):
    id: int
    user_id: int
    keyword: str
    result_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)