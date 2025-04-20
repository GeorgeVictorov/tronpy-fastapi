import json

import redis.asyncio as redis
from redis.exceptions import RedisError

from src.config import load_config

config = load_config()
redis_url = config.redis.redis_url

pool: redis.ConnectionPool = redis.ConnectionPool.from_url(url=redis_url, decode_responses=True)
redis_client = redis.Redis(connection_pool=pool)


def get_redis_client() -> redis.Redis:
    return redis_client


async def shutdown_redis():
    await redis_client.aclose()
    await pool.aclose()


async def get_cached_data(r: redis.Redis, key: str) -> dict | None:
    try:
        value = await r.get(key)
        if value:
            return json.loads(value)
        return None
    except (RedisError, json.JSONDecodeError):
        return None


async def set_cached_data(r: redis.Redis, key: str, data, ttl: int = 300):
    try:
        serialized = json.dumps(data)
        await r.set(key, serialized, ex=ttl)
    except RedisError:
        pass
