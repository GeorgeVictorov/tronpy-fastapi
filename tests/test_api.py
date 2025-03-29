import pytest
from src.main import app
from fastapi.testclient import TestClient
from src.ascii_pics import TOTORO
from httpx import ASGITransport, AsyncClient, Response, Request

client = TestClient(app)


def test_welcome_sync():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == TOTORO


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


class FailingTransport(ASGITransport):
    async def handle_async_request(self, request: Request) -> Response:
        return Response(503, json={"detail": "Service Unavailable"})


@pytest.fixture
async def failing_client():
    async with AsyncClient(transport=FailingTransport(app), base_url="http://test") as ac:
        yield ac


async def test_welcome_async(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.text == TOTORO


async def test_service_unavailable(failing_client):
    response = await failing_client.get("/")
    assert response.status_code == 503
    assert response.json() == {"detail": "Service Unavailable"}
