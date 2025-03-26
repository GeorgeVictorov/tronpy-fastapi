from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db, init_db
from src.tron import get_tron_account_info
from src.crud import save_request, get_requests
from src.schemas import TronRequestCreate, TronRequestResponse
import sys
from contextlib import asynccontextmanager


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(a: FastAPI):
    try:
        init_db()
        yield
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


app = FastAPI(lifespan=lifespan) # run -> uvicorn src.main:app


@app.post("/add_record", response_model=TronRequestResponse)
def get_tron_info(request: TronRequestCreate, db: Session = Depends(get_db)):
    try:
        data = get_tron_account_info(request.address)

        if not data:
            raise HTTPException(status_code=404, detail="Data for the given address not found")

        saved = save_request(db, request.address, data["balance"], data["bandwidth"], data["energy"])
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/records")
def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        records = get_requests(db, skip, limit)
        if not records:
            raise HTTPException(status_code=404, detail="No records found")
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
