from typing import Literal
from uuid import uuid7, UUID

from sqlalchemy import ForeignKey, Enum, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    post_id: Mapped[UUID | None] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'))
    comment_id: Mapped[UUID | None] = mapped_column(ForeignKey('comments.id', ondelete='CASCADE'))
    type: Mapped[Literal['LIKE', 'DISLIKE']] = mapped_column(Enum('LIKE', 'DISLIKE', name='vote_type_enum'), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'author_id',
            'post_id',
            'comment_id',
            name='uq_vote_author_target',
            postgresql_nulls_not_distinct=True
        ),
        CheckConstraint(
            '(post_id IS NULL) != (comment_id IS NULL)',
            name='ck_vote_target'
        ),
        Index(
            'ix_vote_post_id',
            'post_id',
            postgresql_where=(post_id.is_not(None)),
        ),
        Index(
            'ix_vote_comment_id',
            'comment_id',
            postgresql_where=(comment_id.is_not(None)),
        )
    )