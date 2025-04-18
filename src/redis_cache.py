import json
import redis.asyncio as redis
from redis.exceptions import RedisError
from src.config import load_config

config = load_config()
redis_url = config.redis.redis_url

redis_client: redis.Redis | None = None


async def startup_redis():
    global redis_client
    redis_client = redis.from_url(redis_url, decode_responses=True)


async def shutdown_redis():
    await redis_client.close()


def get_redis() -> redis.Redis:
    return redis_client


async def get_cached_data(r: redis.Redis, key: str) -> dict | None:
    try:
        value = await r.get(key)
        if value:
            return json.loads(value)
        return None
    except (RedisError, json.JSONDecodeError):
        return None


async def set_cached_data(r: redis.Redis, key: str, value: dict, ttl: int = 300):
    try:
        serialized = json.dumps(value)
        await r.set(key, serialized, ex=ttl)
    except RedisError:
        pass
