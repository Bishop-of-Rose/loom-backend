from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

class ProfileInit(BaseModel):
    username: str

class ProfileChange(BaseModel):
    username: str | None

class MinProfileResponse(BaseModel):
    id: UUID
    username: str
    avatar: str

class ProfileResponse(BaseModel):
    id: UUID
    username: str
    avatar: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True