from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from ..models import User, Connection
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/connect',
    tags=['Connections'],
)

@router.post('/to:{connector_id}')
def initiate_connection(connector_id: UUID,
                        current_user: User = Depends(get_current_user),
                        session: Session = Depends(get_session)):
    if current_user.id == connector_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User initiating connection to self')

    connection = Connection(initiator_id=current_user.id, recipient_id=connector_id)
    try:
        session.add(connection)
        session.commit()

    except IntegrityError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Recipient not found')

        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User already has a connection with this recipient')

    return

@router.post('/from:{connector_id}')
def receive_connection(connector_id: UUID,
                       current_user: User = Depends(get_current_user),
                       session: Session = Depends(get_session)):
    if current_user.id == connector_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User receiving connection from self')

    u1, u2 = sorted([connector_id, current_user.id])

    connection = session.get(Connection, (u1, u2))
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Connection request not found')

    if connection.initiator_id != connector_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User receiving self initiated connection')

    connection.is_active = True
    session.commit()

    return


