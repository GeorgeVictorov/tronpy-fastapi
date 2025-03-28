import sys
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.ascii_pics import TOTORO
from src.crud import get_records, save_request
from src.database import get_db, init_db
from src.schemas import TronRequestCreate, TronRequestResponse
from src.tron import get_tron_account_info


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(a: FastAPI):
    try:
        await init_db()
        yield
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


app = FastAPI()  # run -> uvicorn src.main:app


@app.post("/add_record", response_model=TronRequestResponse)
async def get_tron_info(request: TronRequestCreate, db: AsyncSession = Depends(get_db)) -> TronRequestResponse:
    try:
        data = await get_tron_account_info(request.address)

        if not data:
            raise HTTPException(status_code=404, detail="No data for address")

        saved = await save_request(db, request.address, data["balance"], data["bandwidth"], data["energy"])
        return saved
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/records")
async def get_history(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)) -> List[TronRequestResponse]:
    try:
        records = await get_records(db, skip, limit)
        if not records:
            raise HTTPException(status_code=404, detail="No records found")
        return records
    except Exception:
        raise


@app.get("/", response_class=PlainTextResponse)
async def welcome():
    return TOTORO
