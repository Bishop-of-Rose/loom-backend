from typing import Generic, TypeVar, List

from pydantic import BaseModel

T = TypeVar('T')

class QueryMeta(BaseModel):
    prev_cursor: str | None
    next_cursor: str | None

class QueryResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: QueryMeta

    class Config:
        from_attributes = True