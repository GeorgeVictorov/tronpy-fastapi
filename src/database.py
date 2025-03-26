from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import load_config
from src.models import Base

DATABASE_URL = load_config().db.database_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
