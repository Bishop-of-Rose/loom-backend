from fastapi import status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['50/minute']
)

def rate_limit_exceeded_handler(exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        headers={'Retry-After': exc.detail},
        content={'detail': 'Rate limit exceeded'}
    )