from pydantic import BaseModel


class TronRequestCreate(BaseModel):
    address: str


class TronRequestResponse(TronRequestCreate):
    balance: int
    bandwidth: int
    energy: int
