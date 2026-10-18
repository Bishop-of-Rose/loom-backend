from uuid import uuid7, UUID
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .profiles import Profile

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str | None] = mapped_column()
    google_id: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    profile: Mapped[Profile | None] = relationship(
        'Profile',
        lazy='joined',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )