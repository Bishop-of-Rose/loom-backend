from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import ForeignKeyViolation, CheckViolation

from ..models import User, Connection
from ..core.database import get_session
from ..core.dependencies import get_current_user

router = APIRouter(
    prefix='/connect',
    tags=['Connections'],
)

@router.post('/{user_id}')
def initiate_connection(user_id: UUID,
                        current_user: User = Depends(get_current_user),
                        session: Session = Depends(get_session)):
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User and recipient are the same')

    connection = session.get(Connection, sorted([current_user.id, user_id]))
    if connection is not None:
        if connection.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Connection already established')

        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Connection already requested')

    connection = Connection(initiator_id=current_user.id, recipient_id=user_id)
    try:
        session.add(connection)
        session.commit()

    except IntegrityError as e:
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Recipient not found')

    return {'message': 'Connection successfully requested'}

@router.put('/{user_id}')
def receive_connection(user_id: UUID,
                       current_user: User = Depends(get_current_user),
                       session: Session = Depends(get_session)):
    connection = session.get(Connection, sorted([current_user.id, user_id]))
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Connection not found')

    if connection.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Connection already established')

    connection.is_active = True
    session.commit()
    return {'message': 'Connection successfully established'}

@router.delete('/{user_id}')
def delete_connection(user_id: UUID,
                      current_user: User = Depends(get_current_user),
                      session: Session = Depends(get_session)):
    connection = session.get(Connection, sorted([current_user.id, user_id]))
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Connection not found')

    session.delete(connection)
    session.commit()
    return {'message': 'Connection successfully deleted'}