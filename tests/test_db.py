import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.crud import get_records, save_request
from src.models import TronRequest


@pytest.fixture
async def mock_db():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False, future=True)
    session_local = async_sessionmaker(engine)

    async with engine.begin() as conn:
        await conn.run_sync(TronRequest.metadata.create_all)

    async with session_local() as db:
        yield db


async def test_save_request(mock_db):
    address = "fake_address"
    balance = 100
    bandwidth = 256
    energy = 10000

    saved_entry = await save_request(mock_db, address, balance, bandwidth, energy)

    assert saved_entry.address == address
    assert saved_entry.balance == balance
    assert saved_entry.bandwidth == bandwidth
    assert saved_entry.energy == energy

    result = await mock_db.execute(select(TronRequest).filter_by(address=address))
    record = result.scalar_one_or_none()
    assert record is not None
    assert record.address == address
    assert record.balance == balance
    assert record.bandwidth == bandwidth
    assert record.energy == energy


async def test_get_records(mock_db):
    await save_request(mock_db, "address_1", 100, 256, 10000)
    await save_request(mock_db, "address_2", 200, 512, 20000)

    records = await get_records(mock_db)

    assert len(records) == 2
    assert records[0].address == "address_1"
    assert records[1].address == "address_2"


@pytest.mark.asyncio
async def test_get_records_empty(mock_db):
    records = await get_records(mock_db)
    assert records == []
