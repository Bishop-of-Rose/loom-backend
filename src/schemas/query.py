from typing import Generic, TypeVar, List

from pydantic import BaseModel

T = TypeVar('T')

class QueryResponse(BaseModel, Generic[T]):
    data: List[T]
    cursor: str | None

    class Config:
        from_attributes = True