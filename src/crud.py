from sqlalchemy.orm import Session

from src.models import TronRequest


def save_request(db: Session, address: str, balance: int, bandwidth: int, energy: int):
    db_entry = TronRequest(address=address, balance=balance, bandwidth=bandwidth, energy=energy)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_records(db: Session, skip: int = 0, limit: int = 10):
    return db.query(TronRequest).order_by(TronRequest.created_at.desc()).offset(skip).limit(limit).all()
