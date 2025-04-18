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

from src.redis_cache import get_redis, get_cached_data, set_cached_data


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
async def get_history(skip: int = 0,
                      limit: int = 10,
                      db: AsyncSession = Depends(get_db),
                      redis_client=Depends(get_redis)
                      ) -> List[TronRequestResponse]:
    cache_key = f"records:{skip}:{limit}"
    cached = await get_cached_data(redis_client, cache_key)
    if cached:
        return [TronRequestResponse(**item) for item in cached]

    try:
        records = await get_records(db, skip, limit)
        if not records:
            raise HTTPException(status_code=404, detail="No records found")
        response_models = [TronRequestResponse.from_orm(r).dict() for r in records]
        print(response_models)
        return records
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/", response_class=PlainTextResponse)
async def welcome():
    return TOTORO
