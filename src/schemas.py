from pydantic import BaseModel, ConfigDict, Field


class TronRequestCreate(BaseModel):
    address: str = Field(..., min_length=1)



class TronRequestResponse(TronRequestCreate):
    balance: int | None
    bandwidth: int | None
    energy: int | None

    model_config = ConfigDict(from_attributes=True)
