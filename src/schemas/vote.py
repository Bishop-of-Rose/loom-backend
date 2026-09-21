from typing import Literal
from uuid import UUID

from pydantic import BaseModel, model_validator

class VoteBase(BaseModel):
    post_id: UUID | None = None
    comment_id: UUID | None = None

    @model_validator(mode="after")
    def vote_src(self):
        has_comment = self.comment_id is not None
        has_post = self.post_id is not None

        if has_comment == has_post:
            raise ValueError("Vote reference <post_id | comment_id> can not be both or neither.")

        return self

class VoteCreate(VoteBase):
    type: Literal["LIKE","DISLIKE"]

class VoteUpdate(VoteBase):
    type: Literal["LIKE","DISLIKE"]