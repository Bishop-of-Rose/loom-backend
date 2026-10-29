from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class SearchMeta(BaseModel):
    missing: list[UUID]

class SearchResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: SearchMeta

    model_config = ConfigDict(from_attributes=True)