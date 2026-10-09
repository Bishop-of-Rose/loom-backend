from uuid import UUID

from pydantic import BaseModel, model_validator

class VoteBase(BaseModel):
    post_id: UUID | None
    comment_id: UUID | None

    @model_validator(mode='after')
    def ck_comment_target(self):
        if (self.post_id is None) == (self.comment_id is None):
            raise ValueError('Vote can either only target a post or a comment')

        return self