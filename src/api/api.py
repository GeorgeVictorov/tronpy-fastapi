import logging
from typing import List

from fastapi import Depends, HTTPException
from fastapi.background import BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from tronpy.exceptions import AddressNotFound

from src.ascii_pics import TOTORO
from src.crud import get_records, save_request
from src.database import get_db
from src.main import app
from src.redis_cache import get_cached_data, get_redis_client, set_cached_data
from src.schemas import TronRequestCreate, TronRequestResponse
from src.tron import get_tron_account_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/add_record", response_model=TronRequestResponse)
async def get_tron_info(request: TronRequestCreate,
                        db: AsyncSession = Depends(get_db),
                        redis_client=Depends(get_redis_client)
                        ) -> TronRequestResponse:
    try:
        data = await get_tron_account_info(request.address)

        saved = await save_request(db, request.address, data["balance"], data["bandwidth"], data["energy"])

        keys = await redis_client.keys("records-*")

        if keys:
            logger.info(f'Deleting cache -> keys: {keys}')
            await redis_client.delete(*keys)

        return saved

    except AddressNotFound:
        raise HTTPException(status_code=404, detail="No data for address")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/records")
async def get_history(background_tasks: BackgroundTasks,
                      skip: int = 0,
                      limit: int = 10,
                      db: AsyncSession = Depends(get_db),
                      redis_client=Depends(get_redis_client),
                      ) -> List[TronRequestResponse]:
    cache_key = f'records-{skip}-{limit}'
    cached = await get_cached_data(redis_client, cache_key)
    if not cached:
        try:
            records = await get_records(db, skip, limit)
            if not records:
                raise HTTPException(status_code=404, detail="No records found")
            response = [TronRequestResponse.model_validate(record).model_dump() for record in records]

            background_tasks.add_task(set_cached_data, redis_client, cache_key, response, 150)
            return records
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Internal Server Error")
    return [TronRequestResponse(**item) for item in cached]


@app.get("/", response_class=PlainTextResponse)
async def welcome():
    return TOTORO
