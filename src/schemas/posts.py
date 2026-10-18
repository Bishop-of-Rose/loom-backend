from datetime import datetime
from typing import Set
from uuid import UUID

from pydantic import BaseModel

from .profiles import MinProfileResponse

class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(BaseModel):
    title: str |  None = None
    content: str | None = None

class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    media: Set[str]
    likes_count: int
    dislikes_count: int
    created_at: datetime
    updated_at: datetime
    author: MinProfileResponse