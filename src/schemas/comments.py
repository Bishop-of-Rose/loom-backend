from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from .profiles import MinProfileResponse

class CommentCreate(BaseModel):
    commented: UUID | None = None
    replied: UUID | None = None
    content: str

    @model_validator(mode='after')
    def ck_comment_target(self):
        if self.commented is None == self.replied is None:
            raise ValueError('Comment can either only target a post or a comment')

        return self

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: UUID
    commented: UUID | None
    replied: UUID | None
    content: str
    media: set[str]
    likes_count: int
    dislikes_count: int
    created_at: datetime
    updated_at: datetime
    author: MinProfileResponse

    model_config = ConfigDict(from_attributes=True)