from uuid import UUID

from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

class Connection(Base):
    __tablename__ = "connections"

    person_one: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), primary_key=True)
    person_two: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), primary_key=True)
    initiator_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    recipient_id: Mapped[UUID] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        CheckConstraint('person_one < person_two', name='ck_uuid_order'),
        CheckConstraint('initiator_id != recipient_id', name='ck_no_self_connection'),
        CheckConstraint(
            '(initiator_id = person_one AND recipient_id = person_two) OR '
            '(initiator_id = person_two AND recipient_id = person_one)',
            name='ck_initiator_recipient_match_pk'
        )
    )

    def __init__(self, initiator_id: UUID, recipient_id: UUID, **kwargs):
        u1, u2 = sorted([initiator_id, recipient_id])
        super().__init__(
            person_one=u1,
            person_two=u2,
            initiator_id=initiator_id,
            recipient_id=recipient_id,
            **kwargs
        )