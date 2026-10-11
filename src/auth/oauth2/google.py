from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ...models import User
from ...services import get_user_by_email, get_user_by_oauth
from ...core.database import get_session
from ...core.config import settings
from ...core.limiter import limiter
from ...util.security import create_tokens

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

router = APIRouter(
    prefix='/auth/google',
    tags=['Google OAuth2']
)

@router.get('/login')
@limiter.limit('5/minute')
async def google_login(request: Request):
    redirect_uri = 'http://localhost:10000/auth/google/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/callback')
@limiter.limit('5/minute')
async def google_callback(request: Request, response: Response, session: Session = Depends(get_session)):
    try:
        token = await oauth.google.authorize_access_token(request)

    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Google OAuth login failed: {e}')

    userinfo = token.get('userinfo')
    if not userinfo or not userinfo.get('sub') or not userinfo.get('email') or not userinfo.get('name'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Failed to fetch Google user info')


    user = get_user_by_oauth(session, userinfo['sub'], 'google')
    if not user:
        user = get_user_by_email(session, userinfo['email'])
        if user:
            user.oauth_id = userinfo['sub']
            user.provider = 'google'
            session.commit()

        else:
            user = User(
                email=userinfo['email'],
                oauth_id=userinfo['sub'],
                provider='google'
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