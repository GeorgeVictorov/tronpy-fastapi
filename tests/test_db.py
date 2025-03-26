import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.crud import get_records, save_request
from src.models import Base, TronRequest

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def db():
    init_db()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_save_request(db: Session):
    test_address = "TXYZ...123"
    test_balance = 1000
    test_bandwidth = 500
    test_energy = 300

    saved_request = save_request(db, test_address, test_balance, test_bandwidth, test_energy)

    assert saved_request.address == test_address
    assert saved_request.balance == test_balance
    assert saved_request.bandwidth == test_bandwidth
    assert saved_request.energy == test_energy

    db_request = db.query(TronRequest).filter(TronRequest.address == test_address).first()
    assert db_request is not None
    assert db_request.address == test_address


def test_get_record(db: Session):
    records = get_records(db)

    assert isinstance(records, list)
