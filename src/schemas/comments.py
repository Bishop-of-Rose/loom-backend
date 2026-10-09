from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, model_validator

from .profiles import MinProfileResponse

class CommentCreate(BaseModel):
    commented: UUID | None
    replied: UUID | None
    content: str
    media: List[str] = []

    @model_validator(mode='after')
    def ck_comment_target(self):
        if self.commented is None == self.replied is None:
            raise ValueError('Comment can either only target a post or a comment')

        return self

class CommentUpdate(BaseModel):
    content: str
    media: List[str] = []

class CommentResponse(BaseModel):
    id: UUID
    commented: UUID | None
    replied: UUID | None
    content: str
    media: List[str] = []
    likes: List[UUID]
    dislikes: List[UUID]
    created_at: datetime
    updated_at: datetime
    author: MinProfileResponse

    class Config:
        from_attributes = True