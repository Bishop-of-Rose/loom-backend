from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, users, posts, comments, connections, vote
from .core.config import settings
from .core.limiter import limiter, RateLimitExceeded, rate_limit_exceeded_handler

app = FastAPI(
    title='Loom',
    version='1.0.0'
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGIN,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(connections.router)
app.include_router(vote.router)

@app.get('')
def root():
    return {'message': 'Application currently running'}
