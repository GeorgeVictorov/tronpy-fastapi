from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()


class TronRequest(Base):
    __tablename__ = "tron_requests"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    balance = Column(Integer)
    bandwidth = Column(Integer)
    energy = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
