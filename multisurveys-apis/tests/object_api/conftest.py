import pytest
from fastapi.testclient import TestClient

from object_api.api import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
