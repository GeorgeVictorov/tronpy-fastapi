import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class PostgresConfig:
    database_url: str


@dataclass
class Config:
    db: PostgresConfig


def load_config() -> Config:
    load_dotenv()

    return Config(
        PostgresConfig(
            database_url=os.getenv("DATABASE_URL"),
        )
    )
