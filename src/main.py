import sys
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.crud import get_records, save_request
from src.database import get_db, init_db
from src.schemas import TronRequestCreate, TronRequestResponse
from src.tron import get_tron_account_info


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(a: FastAPI):
    try:
        init_db()
        yield
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


app = FastAPI(lifespan=lifespan)  # run -> uvicorn src.main:app


@app.post("/add_record", response_model=TronRequestResponse)
def get_tron_info(request: TronRequestCreate, db: Session = Depends(get_db)) -> TronRequestResponse:
    try:
        data = get_tron_account_info(request.address)

        if not data:
            raise HTTPException(status_code=404, detail="No data for address")

        saved = save_request(db, request.address, data["balance"], data["bandwidth"], data["energy"])
        return saved
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/records")
def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> List[TronRequestResponse]:
    try:
        records = get_records(db, skip, limit)
        if not records:
            raise HTTPException(status_code=404, detail="No records found")
        return records
    except Exception:
        raise
