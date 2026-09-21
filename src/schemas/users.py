from typing import List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    initiated_connections: List[UUID]
    received_connections: List[UUID]
    established_connections: List[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
