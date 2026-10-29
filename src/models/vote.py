from typing import Literal
from uuid import UUID, uuid7

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Vote(Base):
    __tablename__ = 'votes'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'))
    post_id: Mapped[UUID | None] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'))
    comment_id: Mapped[UUID | None] = mapped_column(ForeignKey('comments.id', ondelete='CASCADE'))
    type: Mapped[Literal['LIKE', 'DISLIKE']] = mapped_column(Enum('LIKE', 'DISLIKE', name='vote_type_enum'))

    __table_args__ = (
        CheckConstraint(
            '(post_id IS NULL) != (comment_id IS NULL)', name='ck_vote_target'
        ),
        UniqueConstraint(
            'author_id',
            'post_id',
            'comment_id',
            name='uq_vote_author_target',
            postgresql_nulls_not_distinct=True,
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
        ),
    )