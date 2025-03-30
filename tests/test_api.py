from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient, Request, Response
from tronpy.exceptions import AddressNotFound

from src.ascii_pics import TOTORO
from src.database import get_db
from src.main import app

client_sync = TestClient(app)


def test_welcome_sync():
    response = client_sync.get("/")
    assert response.status_code == 200
    assert response.text == TOTORO


@pytest.fixture
async def async_client(transport=None):
    transport = transport or ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class FailingTransport(ASGITransport):
    async def handle_async_request(self, request: Request) -> Response:
        return Response(503, json={"detail": "Service Unavailable"})


@pytest.fixture
def override_get_db():
    mock_db = AsyncMock()

    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db
    return mock_db


async def test_welcome_async(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.text == TOTORO


async def test_service_unavailable(async_client):
    async with AsyncClient(transport=FailingTransport(app), base_url="http://test") as failing_client:
        response = await failing_client.get("/")
        assert response.status_code == 503
        assert response.json() == {"detail": "Service Unavailable"}


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


async def test_get_tron_info_success(override_get_db, mocker, async_client):
    mock_data = {"address": "fake_address", "balance": 100, "bandwidth": 256, "energy": 10000}

    mocker.patch("src.api.api.get_tron_account_info", AsyncMock(return_value=mock_data))
    mocker.patch("src.api.api.save_request", AsyncMock(return_value=mock_data))

    request_payload = {"address": "fake_address"}

    response = await async_client.post("/add_record", json=request_payload)

    assert response.status_code == 200
    assert response.json() == mock_data


async def test_get_tron_info_no_data_on_address(override_get_db, mocker, async_client):
    mock_data = {"address": "fake_address", "balance": 100, "bandwidth": 256, "energy": 10000}

    mocker.patch("src.api.api.get_tron_account_info", AsyncMock(side_effect=AddressNotFound()))
    mocker.patch("src.api.api.save_request", AsyncMock(return_value=mock_data))

    request_payload = {"address": "fake_address"}

    response = await async_client.post("/add_record", json=request_payload)

    assert response.status_code == 404
    assert response.json() == {'detail': 'No data for address'}
