import pytest
from src.main import app
from fastapi.testclient import TestClient
from src.ascii_pics import TOTORO
from httpx import ASGITransport, AsyncClient

client = TestClient(app)


def test_welcome_sync():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == TOTORO


@pytest.mark.asyncio
async def test_welcome_async():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.text == TOTORO
