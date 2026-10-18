from uuid import UUID
from datetime import datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Profile(Base):
    __tablename__ = 'profiles'

    id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    avatar: Mapped[str] = mapped_column(default='')
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())