from uuid import UUID

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Connection(Base):
    __tablename__ = "connections"

    user_id_1: Mapped[UUID] = mapped_column(primary_key=True)
    user_id_2: Mapped[UUID] = mapped_column(primary_key=True)
    initiator_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        CheckConstraint('user_id_1 < user_id_2', name='ck_uuid_order'),
        CheckConstraint('initiator_id != recipient_id', name='ck_no_self_connection'),
        CheckConstraint(
            '(initiator_id = user_id_1 AND recipient_id = user_id_2) OR '
            '(initiator_id = user_id_2 AND recipient_id = user_id_1)',
            name='ck_initiator_recipient_match_pk'
        )
    )

    def __init__(self, initiator_id: UUID, recipient_id: UUID, **kwargs):
        u1, u2 = sorted([initiator_id, recipient_id])
        super().__init__(
            user_id_1=u1,
            user_id_2=u2,
            initiator_id=initiator_id,
            recipient_id=recipient_id,
            **kwargs
        )