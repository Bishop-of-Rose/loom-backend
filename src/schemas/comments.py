from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from .users import UserResponse

class CommentCreate(BaseModel):
    post_id: UUID
    content: str

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    content: str
    likes: List[UUID]
    dislikes: List[UUID]
    created_at: datetime
    updated_at: datetime
    author: UserResponse

    class Config:
        from_attributes = True