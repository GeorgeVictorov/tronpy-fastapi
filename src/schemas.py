from pydantic import BaseModel


class TronRequestCreate(BaseModel):
    address: str


class TronRequestResponse(TronRequestCreate):
    balance: int | None
    bandwidth: int | None
    energy: int | None

    class Config:
        from_attributes = True
