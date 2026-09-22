from typing import Generic, TypeVar, List
from uuid import UUID

from pydantic import BaseModel

T = TypeVar('T')

class SearchResponse(BaseModel, Generic[T]):
    data: List[T]
    missing: List[UUID]

    class Config:
        from_attributes = True