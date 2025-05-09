from sqlalchemy.ext.asyncio import (AsyncEngine, async_sessionmaker,
                                    create_async_engine)

from src.config import load_config
from src.models import Base

config = load_config()
db_url = config.db.database_url

engine: AsyncEngine = create_async_engine(db_url)
session_local = async_sessionmaker(engine)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    db = session_local()
    try:
        yield db
    finally:
        await db.close()
