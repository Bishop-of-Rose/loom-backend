from typing import List
from uuid import uuid7, UUID
from datetime import datetime

from sqlalchemy import ForeignKey, func, CheckConstraint, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .profiles import Profile
from .vote import Vote

class Comment(Base):
    __tablename__ =  "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    commented: Mapped[UUID | None] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'))
    replied: Mapped[UUID | None] = mapped_column(ForeignKey('comments.id', ondelete='CASCADE'))
    content: Mapped[str] = mapped_column(nullable=False)
    media: Mapped[List[str]] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped['Profile'] = relationship(
        'Profile',
        lazy='joined',
        viewonly=True
    )
    _votes: Mapped[List['Vote']] = relationship(
        'Vote',
        lazy='selectin',
        viewonly=True
    )

    @property
    def likes(self) -> List[UUID]:
        return [vote.author_id for vote in self._votes if vote.type == 'LIKE']

    @property
    def dislikes(self) -> List[UUID]:
        return [vote.author_id for vote in self._votes if vote.type == 'DISLIKE']

    __table_args__ = (
        CheckConstraint(
            '(commented IS NULL) != (replied IS NULL)',
            name='ck_comment_target'
        ),
    )