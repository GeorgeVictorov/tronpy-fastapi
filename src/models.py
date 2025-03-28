from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TronRequest(Base):
    __tablename__ = "tron_requests"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    balance = Column(Integer)
    bandwidth = Column(Integer)
    energy = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
