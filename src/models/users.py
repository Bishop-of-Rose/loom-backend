from typing import List
from uuid import uuid7, UUID
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from .connections import Connection

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    _connections: Mapped[List['Connection']] = relationship(
        'Connection',
        primaryjoin='''or_(
            User.id == Connection.initiator_id, User.id == Connection.recipient_id
        )''',
        viewonly=True
    )

    @property
    def initiated_connections(self) -> List[UUID]:
        return [connection.recipient_id
                for connection in self._connections
                if connection.initiator_id == self.id and connection.is_active == False]

    @property
    def received_connections(self) -> List[UUID]:
        return [connection.initiator_id
                for connection in self._connections
                if connection.recipient_id == self.id and connection.is_active == False]

    @property
    def established_connections(self) -> List[UUID]:
        return [connection.recipient_id
                if connection.initiator_id == self.id
                else connection.initiator_id
                for connection in self._connections
                if connection.is_active == True]