import pytest
from unittest.mock import patch

from app.services.state_manager import state_manager
from tests.mocked_data import USER1, USER3, CHAT_ID


@pytest.fixture
def mock_state_manager():
    with patch("app.state.state_manager") as mock:
        yield mock


def test_websocket_endpoint(mock_app):
    # Verify empty dict on init 
    assert not state_manager._active_chats

    with mock_app.websocket_connect(f"/ws_test/{CHAT_ID}/{USER1.id}") as websocket1:
        with mock_app.websocket_connect(f"/ws_test/{CHAT_ID}/{USER3.id}") as websocket2:
            # Test Connection
            assert len(state_manager._active_chats.keys()) == 1 and len(state_manager.get_active_chat(CHAT_ID)) == 2
            
            websocket1.send_text(f"Hello from {USER1.id}")
            received = websocket2.receive_text()
            assert received == f"User {USER1.id}: Hello from {USER1.id}"

            websocket2.send_text(f"Hi {USER1.id}, this is {USER3.id}")
            received = websocket1.receive_text()
            assert received == f"User {USER3.id}: Hi {USER1.id}, this is {USER3.id}"

            # Test Disconnection
            websocket1.close()
            received = websocket2.receive_text()
            assert received == f"User {USER1.id} has left the chat"
            assert len(state_manager._active_chats.keys()) == 1 and len(state_manager.get_active_chat(CHAT_ID)) == 1
    # Verify cleanup on disconnection
    assert not state_manager._active_chats
