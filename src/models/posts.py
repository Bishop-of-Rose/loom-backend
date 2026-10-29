from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy import ARRAY, ForeignKey, String, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from . import Base
from .profiles import Profile
from .vote import Vote

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    media: Mapped[set[str]] = mapped_column(ARRAY(String), default=[])
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped[Profile] = relationship('Profile', lazy='joined', viewonly=True)
    likes_count: Mapped[int] = column_property(
        select(func.count(Vote.id))
        .where(Vote.post_id == id)
        .where(Vote.type == 'LIKE')
        .correlate_except(Vote)
        .scalar_subquery()
    )
    dislikes_count: Mapped[int] = column_property(
        select(func.count(Vote.id))
        .where(Vote.post_id == id)
        .where(Vote.type == 'DISLIKE')
        .correlate_except(Vote)
        .scalar_subquery()
    )