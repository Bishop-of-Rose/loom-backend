from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from .profiles import ProfileResponse

class PostCreate(BaseModel):
    content: str
    tags: List[str] = []
    media: List[str] = []

class PostUpdate(BaseModel):
    content: str
    tags: List[str] = []
    media: List[str] = []

class PostResponse(BaseModel):
    id: UUID
    content: str
    tags: List[str] = []
    media: List[str] = []
    likes: List[UUID]
    dislikes: List[UUID]
    created_at: datetime
    updated_at: datetime
    author: ProfileResponse