from fastapi.testclient import TestClient

from src.config import load_config
from src.main import app

client = TestClient(app)


def test_add_record():
    test_address = load_config().tron.base58_address  # test address

    response = client.post("/add_record", json={"address": test_address})

    assert response.status_code == 200
    data = response.json()
    assert "address" in data
    assert "balance" in data
    assert "bandwidth" in data
    assert "energy" in data


def test_get_history():
    response = client.get("/records?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
