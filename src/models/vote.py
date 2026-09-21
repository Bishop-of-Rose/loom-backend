from typing import Literal
from uuid import uuid7, UUID

from sqlalchemy import ForeignKey, Enum, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id: Mapped[UUID | None] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'))
    comment_id: Mapped[UUID | None] = mapped_column(ForeignKey('comments.id', ondelete='CASCADE'))
    type: Mapped[Literal['LIKE', 'DISLIKE']] = mapped_column(Enum('LIKE', 'DISLIKE', name='vote_type_enum'), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'post_id'),
        UniqueConstraint('user_id', 'comment_id'),
        CheckConstraint(
            '(post_id IS NULL) != (comment_id IS NULL)',
            name='ck_vote_target'
        )
    )