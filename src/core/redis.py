import redis

from .config import settings

client = redis.from_url(settings.REDIS_URL)