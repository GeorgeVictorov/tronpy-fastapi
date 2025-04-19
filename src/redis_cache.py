import json
import inspect
from functools import wraps
import redis.asyncio as redis
from redis.exceptions import RedisError
from src.config import load_config
from src.schemas import TronRequestResponse

config = load_config()
redis_url = config.redis.redis_url

pool: redis.ConnectionPool = redis.ConnectionPool.from_url(url=redis_url, decode_responses=True)
redis_client = redis.Redis(connection_pool=pool)


def get_redis_client() -> redis.Redis:
    return redis_client


async def shutdown_redis():
    await redis_client.aclose()
    await pool.aclose()


def build_cache_key(func, args, kwargs):
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()

    key_parts = [func.__name__]
    for k, v in bound.arguments.items():
        if k in {"db", "redis_client"}:
            continue
        key_parts.append(f"{k}={v}")
    return ":".join(key_parts)


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


def redis_cache(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = build_cache_key(func, args, kwargs)

            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    print(f"[Redis] Cache hit: {cache_key}")
                    return json.loads(cached)
            except RedisError:
                pass

            result = await func(*args, **kwargs)

            try:
                response = [TronRequestResponse.model_validate(r).model_dump() for r in result]
                await redis_client.set(cache_key, response, ex=ttl)
                print(f"[Redis] Cache set: {cache_key}")
            except RedisError:
                pass

            return result

        return wrapper

    return decorator
