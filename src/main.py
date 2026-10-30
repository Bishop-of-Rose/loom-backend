import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from . import auth
from .core.config import settings
from .core.limiter import limiter
from .routers import account, comments, posts, profiles, query, search, vote

app = FastAPI(
    title='Loom',
    version='1.0.0',
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()
    process_time = end_time - start_time

    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGIN,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site='lax',
    https_only=False,
)

app.include_router(auth.default.router)
app.include_router(auth.google.router)
app.include_router(account.router)
app.include_router(profiles.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(vote.router)
app.include_router(query.router)
app.include_router(search.router)

@app.get('/', tags=['Health'])
def root():
    return {'message': 'Application currently running'}
