from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .profiles import ProfileResponse

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    updated_at: datetime
    profile: ProfileResponse

    model_config = ConfigDict(from_attributes=True)