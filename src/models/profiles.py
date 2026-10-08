from typing import List
from uuid import UUID
from datetime import datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from . import Base
from .connections import Connection

class Profile(Base):
    __tablename__ = 'profiles'

    id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    avatar: Mapped[str] = mapped_column(default='')
    bio: Mapped[str] = mapped_column(default='')
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    _connections: Mapped[List['Connection']] = relationship(
        'Connection',
        lazy='selectin',
        primaryjoin=lambda: (
            (Profile.id == foreign(Connection.person_one)) | (Profile.id == foreign(Connection.person_two))
        ),
        viewonly=True
    )

    @property
    def connections(self) -> List[UUID]:
        return [connection.recipient_id
                if connection.initiator_id == self.id
                else connection.initiator_id
                for connection in self._connections
                if connection.is_active == True]

    @property
    def initiated(self) -> List[UUID]:
        return [connection.recipient_id
                for connection in self._connections
                if connection.initiator_id == self.id
                and not connection.is_active]

    @property
    def received(self) -> List[UUID]:
        return [connection.initiator_id
                for connection in self._connections
                if connection.recipient_id == self.id
                and not connection.is_active]