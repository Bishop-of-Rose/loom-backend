from typing import List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

class ProfileInit(BaseModel):
    username: str
    bio: str = ""

class ProfileChange(BaseModel):
    username: str | None = None
    bio: str | None = None

class MinProfileResponse(BaseModel):
    id: UUID
    username: str
    bio: str

class ProfileResponse(BaseModel):
    id: UUID
    username: str
    bio: str
    connections: List[UUID]
    initiated: List[UUID]
    received: List[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True