from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from . import auth
from .routers import account, query, search, profiles, posts, comments, connections, vote
from .core.config import settings
from .core.limiter import limiter

app = FastAPI(
    title='Loom',
    version='1.0.0'
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGIN,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site='lax',
    https_only=False
)

app.include_router(auth.default.router)
app.include_router(auth.google.router)
app.include_router(account.router)
app.include_router(query.router)
app.include_router(search.router)
app.include_router(profiles.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(connections.router)
app.include_router(vote.router)

@app.get('/', tags=['Health'])
def root():
    return {'message': 'Application currently running'}
