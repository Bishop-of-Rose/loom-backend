from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr

from .profiles import ProfileResponse

class RegistrationForm(BaseModel):
    email: EmailStr
    password: str

class LoginForm(RegistrationForm):
    pass

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    updated_at: datetime
    profile: ProfileResponse | None

    class Config:
        from_attributes = True