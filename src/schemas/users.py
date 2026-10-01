from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr

from .profiles import ProfileResponse

class RegistrationRequestForm(BaseModel):
    email: EmailStr
    password: str

class ActivationRequestForm(BaseModel):
    email: EmailStr
    token: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    profile: ProfileResponse | None = None

    class Config:
        from_attributes = True