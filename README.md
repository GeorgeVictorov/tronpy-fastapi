# tronpy-fastapi

This is a simple project built with FastAPI to interact with the TRON blockchain.

It includes APIs for retrieving TRON account information, caching data in Redis, and saving data to a PostgreSQL
database.

## Technologies used

- **[fastapi](https://fastapi.tiangolo.com)** - A modern web framework for building APIs with Python
- **[uvicorn](https://www.uvicorn.org)** - ASGI server to run the FastAPI application
- **[tronpy](https://pypi.org/project/tronpy/)** - TRON Python Client Library
- **[asyncpg](https://pypi.org/project/asyncpg/)** - Database interface library designed specifically for PostgreSQL
- **[sqlalchemy[asyncio]](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)** - ORM for asynchronous
  database interactions
- **[redis-py (asyncio)](https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html)** – Redis client for
  async caching using redis.asyncio

## Example Endpoints

### 1. Add TRON Account Info

POST ```/add_record```

#### Request body:

```json
{
  "address": "your_tron_address"
}
```

#### Response:

```json
{
  "address": "your_tron_address",
  "balance": 100,
  "bandwidth": 256,
  "energy": 10000
}
```

### Get TRON Account History

GET ```/records?skip=0&limit=10```

#### Response:

```json
[
  {
    "address": "your_tron_address",
    "balance": 100,
    "bandwidth": 256,
    "energy": 10000,
    "created_at": "2025-03-30T12:00:00"
  }
]
```

## Running tests

To run tests, use ```pytest```:

```
pytest
```