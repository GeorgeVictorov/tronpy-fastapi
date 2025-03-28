from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from src.models import Base
from src.config import load_config

config = load_config()
db_url = config.db.database_url

engine = create_async_engine(db_url)
session_local = async_sessionmaker(engine)


async def init_db(async_engine: AsyncEngine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db = session_local()
    try:
        yield db
    finally:
        await db.close()
