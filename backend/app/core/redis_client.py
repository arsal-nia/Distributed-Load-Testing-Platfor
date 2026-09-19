import os
import redis.asyncio as aioredis
from typing import Optional

_redis_client: Optional[aioredis.Redis] = None

def get_redis_client() -> aioredis.Redis:
    """Return the singleton Redis client."""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = aioredis.from_url(redis_url, decode_responses=True)
    return _redis_client

async def close_redis_client():
    """Close the Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None