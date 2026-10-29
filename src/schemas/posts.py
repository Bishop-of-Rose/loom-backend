from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .profiles import MinProfileResponse

class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    media: set[str]
    likes_count: int
    dislikes_count: int
    created_at: datetime
    updated_at: datetime
    author: MinProfileResponse

    model_config = ConfigDict(from_attributes=True)