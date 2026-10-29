import hashlib
import secrets

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import get_session
from ..core.limiter import limiter
from ..models import User
from ..services import get_user_by_email, get_user_by_oauth
from ..util import whitelist
from ..util.security import create_access_token

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

router = APIRouter(prefix='/auth/google', tags=['Google OAuth2 Authentication'])

@router.get('/login')
@limiter.limit('5/minute')
async def google_login(request: Request):
    redirect_uri = 'http://localhost:10000/auth/google/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/callback')
@limiter.limit('5/minute')
async def google_callback(
    request: Request, response: Response, session: AsyncSession = Depends(get_session)
):
    try:
        token = await oauth.google.authorize_access_token(request)

    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Google OAuth login failed: {e}',
        )

    userinfo = token.get('userinfo')
    if not userinfo or not userinfo.get('sub') or not userinfo.get('email'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Failed to fetch Google user info',
        )

    user = await get_user_by_oauth(session, userinfo['sub'], 'google')
    if not user:
        user = await get_user_by_email(session, userinfo['email'])
        if user:
            user.google_id = userinfo['sub']
            await session.commit()
            await session.refresh(user)

        else:
            user = User(
                email=userinfo['email'],
                google_id=userinfo['sub'],
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

    access_token = create_access_token(user.id)
    refresh_token = secrets.token_hex(32)
    hashed = hashlib.sha256(refresh_token.encode()).hexdigest()
    whitelist.add(hashed, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, user.id)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return {'access_token': access_token}