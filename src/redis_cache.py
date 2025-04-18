import json

import redis.asyncio as redis
from redis.exceptions import RedisError

from src.config import load_config

config = load_config()
redis_url = config.redis.redis_url

r: redis.Redis | None = None


async def connect_to_redis():
    global r
    r = r.from_url(redis_url, decode_responses=True)


async def close_redis():
    await r.close()


async def get_cached_data(key: str) -> dict | None:
    try:
        value = await r.get(key)
        if value:
            return json.loads(value)
        return None
    except (RedisError, json.JSONDecodeError):
        return None


async def set_cached_data(key: str, value: dict, ttl: int = 300):
    try:
        serialized = json.dumps(value)
        await r.set(key, serialized, ex=ttl)
    except RedisError:
        pass
