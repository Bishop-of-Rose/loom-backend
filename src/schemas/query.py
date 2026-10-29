from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class QueryMeta(BaseModel):
    prev_cursor: str | None
    next_cursor: str | None

class QueryResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: QueryMeta

    model_config = ConfigDict(from_attributes=True)