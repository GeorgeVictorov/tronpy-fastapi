import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import init_db


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(a: FastAPI):
    try:
        await init_db()
        yield
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


app = FastAPI()  # run -> uvicorn src.main:app

from src.api import api
