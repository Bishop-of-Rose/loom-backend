from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class MinProfileResponse(BaseModel):
    id: UUID
    username: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)

class ProfileResponse(BaseModel):
    id: UUID
    username: str
    avatar: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)