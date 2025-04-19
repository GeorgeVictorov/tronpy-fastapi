import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import init_db
from src.redis_cache import shutdown_redis


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(a: FastAPI):
    try:
        await init_db()
        yield
        await shutdown_redis()
    except Exception as e:
        print(f"Error during app startup: {e}")
        sys.exit(1)


app = FastAPI()  # run -> uvicorn src.main:app

from src.api import api
