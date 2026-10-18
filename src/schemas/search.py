from typing import Generic, TypeVar, List
from uuid import UUID

from pydantic import BaseModel

T = TypeVar('T')

class SearchMeta(BaseModel):
    missing: List[UUID]

class SearchResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: SearchMeta

    class Config:
        from_attributes = True