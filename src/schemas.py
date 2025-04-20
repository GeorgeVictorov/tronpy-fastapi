from pydantic import BaseModel, ConfigDict


class TronRequestCreate(BaseModel):
    address: str


class TronRequestResponse(TronRequestCreate):
    balance: int | None
    bandwidth: int | None
    energy: int | None

    model_config = ConfigDict(from_attributes=True)
