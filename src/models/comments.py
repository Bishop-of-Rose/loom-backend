from typing import List
from uuid import uuid7, UUID
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .users import User
from .vote import Vote

class Comment(Base):
    __tablename__ =  "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id: Mapped[UUID] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped['User'] = relationship()

    _votes: Mapped[List['Vote']] = relationship(
        'Vote',
        viewonly=True
    )

    @property
    def likes(self) -> List[UUID]:
        return [vote.user_id for vote in self._votes if vote.type == 'LIKE']

    @property
    def dislikes(self) -> List[UUID]:
        return [vote.user_id for vote in self._votes if vote.type == 'DISLIKE']