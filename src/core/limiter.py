from slowapi import Limiter
from slowapi.util import get_ipaddr

limiter = Limiter(
    key_func=get_ipaddr,
    default_limits=['60/minute'],
    headers_enabled=True
)