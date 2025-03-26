from pydantic import BaseModel
from datetime import datetime


class TronRequestCreate(BaseModel):
    address: str


class TronRequestResponse(BaseModel):
    address: str
    balance: int
    bandwidth: int
    energy: int
    requested_at: datetime
