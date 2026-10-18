from typing import Set
from uuid import uuid7, UUID
from datetime import datetime

from sqlalchemy import ForeignKey, func, CheckConstraint, ARRAY, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property

from . import Base
from .profiles import Profile
from .vote import Vote

class Comment(Base):
    __tablename__ =  "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'))
    commented: Mapped[UUID | None] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'))
    replied: Mapped[UUID | None] = mapped_column(ForeignKey('comments.id', ondelete='CASCADE'))
    content: Mapped[str] = mapped_column()
    media: Mapped[Set[str]] = mapped_column(ARRAY(String), default=[])
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped[Profile] = relationship(
        'Profile',
        lazy='joined',
        viewonly=True
    )
    likes_count: Mapped[int] = column_property(
        select(func.count(Vote.id))
        .where(Vote.comment_id == id)
        .where(Vote.type == 'LIKE')
        .correlate_except(Vote)
        .scalar_subquery()
    )
    dislikes_count: Mapped[int] = column_property(
        select(func.count(Vote.id))
        .where(Vote.comment_id == id)
        .where(Vote.type == 'DISLIKE')
        .correlate_except(Vote)
        .scalar_subquery()
    )

    __table_args__ = (
        CheckConstraint(
            '(commented IS NULL) != (replied IS NULL)',
            name='ck_comment_target'
        ),
    )