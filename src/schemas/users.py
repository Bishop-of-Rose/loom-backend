from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

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

    model_config = ConfigDict(from_attributes=True)