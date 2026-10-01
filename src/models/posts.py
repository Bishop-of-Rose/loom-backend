from typing import List
from uuid import uuid7, UUID
from datetime import datetime

from sqlalchemy import ForeignKey, func, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .profiles import Profile
from .vote import Vote

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String))
    media: Mapped[List[str]] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped['Profile'] = relationship('Profile', viewonly=True)
    _votes: Mapped[List['Vote']] = relationship('Vote', viewonly=True)

    @property
    def likes(self) -> List[UUID]:
        return [vote.author_id for vote in self._votes if vote.type == 'LIKE']

    @property
    def dislikes(self) -> List[UUID]:
        return [vote.author_id for vote in self._votes if vote.type == 'DISLIKE']