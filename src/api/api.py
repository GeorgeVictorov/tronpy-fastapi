from typing import List

from fastapi import Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from tronpy.exceptions import AddressNotFound

from src.ascii_pics import TOTORO
from src.crud import get_records, save_request
from src.database import get_db
from src.main import app
from src.schemas import TronRequestCreate, TronRequestResponse
from src.tron import get_tron_account_info


@app.post("/add_record", response_model=TronRequestResponse)
async def get_tron_info(request: TronRequestCreate, db: AsyncSession = Depends(get_db)) -> TronRequestResponse:
    try:
        data = await get_tron_account_info(request.address)

        saved = await save_request(db, request.address, data["balance"], data["bandwidth"], data["energy"])
        return saved

    except AddressNotFound:
        raise HTTPException(status_code=404, detail="No data for address")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/records")
async def get_history(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)) -> List[TronRequestResponse]:
    try:
        records = await get_records(db, skip, limit)
        if not records:
            raise HTTPException(status_code=404, detail="No records found")
        print(records)
        return records
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/", response_class=PlainTextResponse)
async def welcome():
    return TOTORO
