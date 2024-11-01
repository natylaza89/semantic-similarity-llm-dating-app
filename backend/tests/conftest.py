from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings


@pytest.fixture(autouse=True)
def mock_app():
    from app.api.websocket import websocket_endpoint
    app.add_api_websocket_route("/ws_test/{chat_id}/{user_id}", websocket_endpoint)
    client = TestClient(app, base_url="http://testserver" + settings.api_v1_str)
    yield client


@pytest.fixture
def mock_settings():
    with patch("app.utils.settings") as mock:
        yield mock
