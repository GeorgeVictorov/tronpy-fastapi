import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class RedisConfig:
    redis_url: str

@dataclass
class PostgresConfig:
    database_url: str
    test_database_url: str


@dataclass
class Tron:
    base58_address: str
    private_key: str
    api_url: str


@dataclass
class Config:
    redis: RedisConfig
    db: PostgresConfig
    tron: Tron


def load_config() -> Config:
    load_dotenv()

    return Config(
        RedisConfig(
            os.getenv("REDIS_URL"),
        ),
        PostgresConfig(
            database_url=os.getenv("DATABASE_URL"),
            test_database_url=os.getenv("TEST_DATABASE_URL"),
        ),
        Tron(
            base58_address=os.getenv("BASE58CHECK_ADDRESS"),
            private_key=os.getenv("PRIVATE_KEY"),
            api_url=os.getenv("TRON_API_URL"),
        )
    )
