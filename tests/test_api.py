import pytest
from src.main import app
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.ascii_pics import TOTORO
from httpx import ASGITransport, AsyncClient, Response, Request

from src.crud import get_records
from src.database import get_db

client_sync = TestClient(app)


def test_welcome_sync():
    response = client_sync.get("/")
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


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.fixture
def override_get_db(mock_db_session):
    async def mock_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = mock_get_db
    return mock_db_session


async def test_get_history_with_records(override_get_db, mocker, async_client):
    mock_data = [{"address": "fake_address", "balance": 100, "bandwidth": 100, "energy": 10}]

    mocker.patch("src.api.api.get_records", AsyncMock(return_value=mock_data))

    response = await async_client.get("/records?skip=0&limit=10")

    assert response.status_code == 200
    assert response.json() == mock_data


async def test_get_history_no_records(override_get_db, mocker, async_client):
    mocker.patch("src.api.api.get_records", AsyncMock(return_value=[]))

    response = await async_client.get("/records?skip=0&limit=10")

    assert response.status_code == 404
    assert response.json() == {"detail": "No records found"}


async def test_get_history_server_error(override_get_db, mocker, async_client):
    mocker.patch("src.api.api.get_records", AsyncMock(side_effect=Exception("DB error")))

    response = await async_client.get("/records?skip=0&limit=10")

    assert response.status_code == 500


@pytest.mark.parametrize("skip, limit", [(0, 10), (5, 5), (10, 2)])
async def test_get_history_with_pagination(override_get_db, mocker, async_client, skip, limit):
    mock_data = [{"address": "fake_address", "balance": 100, "bandwidth": 100, "energy": 10}]
    mocker.patch("src.api.api.get_records", AsyncMock(return_value=mock_data))

    response = await async_client.get(f"/records?skip={skip}&limit={limit}")

    assert response.status_code == 200
    assert response.json() == mock_data
