from typing import Generic, TypeVar, List

from pydantic import BaseModel

T = TypeVar('T')

class QueryResponse(BaseModel, Generic[T]):
    data: List[T]
    next_cursor: str | None = None
    prev_cursor: str | None = None

    class Config:
        from_attributes = True