from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import TronRequest


async def save_request(db: AsyncSession, address: str, balance: int, bandwidth: int, energy: int):
    db_entry = TronRequest(address=address, balance=balance, bandwidth=bandwidth, energy=energy)
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry


async def get_records(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(TronRequest).order_by(TronRequest.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
