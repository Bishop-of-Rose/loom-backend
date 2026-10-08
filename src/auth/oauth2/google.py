from uuid import uuid7

from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session

from .base import oauth2
from ...models import User, Profile
from ...services import get_user_by_oauth_id, get_user_by_email
from ...core.database import get_session
from ...core.config import settings
from ...core.security import create_tokens
router = APIRouter(
    prefix='/auth/google',
    tags=['Google OAuth2']
)

@router.get('/login')
async def google_login(request: Request):
    redirect_uri = 'http://localhost:10000/auth/google/callback'
    return await oauth2.google.authorize_redirect(request, redirect_uri)

@router.get('/callback')
async def google_callback(request: Request, response: Response, session: Session = Depends(get_session)):
    try:
        token = await oauth2.google.authorize_access_token(request)

    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Google OAuth login failed: {e}')

    userinfo = token.get('userinfo')
    if not userinfo or not userinfo.get('sub') or not userinfo.get('email') or not userinfo.get('name'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Failed to fetch Google user info')


    user = get_user_by_oauth_id(session, userinfo['sub'])
    if not user:
        user = get_user_by_email(session, userinfo['email'])
        if user:
            user.oauth_id = userinfo['sub']
            user.provider = 'google'
            session.commit()

        else:
            user_id = uuid7()
            user = User(
                id=user_id,
                email=userinfo['email'],
                oauth_id=userinfo['sub'],
                provider='google',
                profile=Profile(
                    id=user_id,
                    username=userinfo['name'],
                )
            )

            session.add(user)
            session.commit()
            session.refresh(user)

    access_token, refresh_token = create_tokens(user.id)
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {'access_token': access_token}