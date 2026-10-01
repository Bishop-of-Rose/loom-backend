from typing import List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

class ProfileInit(BaseModel):
    username: str
    avatar: str = ""
    bio: str = ""

class MinProfileResponse(BaseModel):
    id: UUID
    unique_name: str

class ProfileResponse(BaseModel):
    id: UUID
    unique_name: str
    username: str
    avatar: str
    bio: str
    connections: List[UUID]
    initiated: List[UUID]
    received: List[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True