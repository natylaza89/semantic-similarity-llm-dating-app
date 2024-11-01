from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi import status

from app.models.match import MatchRequest
from tests.mocked_data import USER1 as USER, USER2 as MATCHED_USER, CHAT_ID


@pytest.fixture
def mock_state_manager():
    with patch("app.api.users.state_manager") as mock:
        mock.set_user = AsyncMock()
        yield mock


@pytest.fixture
def mock_find_potential_matches():
    with patch("app.api.users.find_potential_match") as mock:
        yield mock


@pytest.fixture
def mock_create_chat_for_matched_users():
    with patch("app.api.users.create_chat_for_matched_users") as mock:
        yield mock


def test_register_new_user(mock_app, mock_state_manager):
    mock_state_manager.get_users.return_value = {}
    response = mock_app.post("/register", json=USER.model_dump())
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "User registered successfully"}
    mock_state_manager.set_user.assert_called_once_with(USER.id, USER)


def test_register_existing_user(mock_app, mock_state_manager):
    mock_state_manager.get_users.return_value = {USER.id: USER}
    
    response = mock_app.post("/register", json=USER.model_dump())
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "User already exists"}


def test_match_user_not_found(mock_app, mock_state_manager):
    mock_state_manager.get_users.return_value = {}
    request = MatchRequest(user_id=USER.id, preferences="King")
    
    response = mock_app.post("/match", json=request.model_dump())
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_match_success(mock_app, mock_state_manager, mock_find_potential_matches, mock_create_chat_for_matched_users):
    mock_state_manager.get_users.return_value = {USER.id: MagicMock()}
    mock_find_potential_matches.return_value = {"match_id": MATCHED_USER.id, "name": MATCHED_USER.name}
    mock_create_chat_for_matched_users.return_value = CHAT_ID
    
    request = MatchRequest(user_id=USER.id, preferences="The best")
    response = mock_app.post("/match", json=request.model_dump())
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "match": {"match_id": MATCHED_USER.id, "name": MATCHED_USER.name},
        "chat_id": CHAT_ID,
        "message": "Potential match found"
    }


def test_match_not_found(mock_app, mock_state_manager, mock_find_potential_matches):
    mock_state_manager.get_users.return_value = {USER.id: MagicMock()}
    mock_find_potential_matches.return_value = None
    
    request = MatchRequest(user_id=USER.id, preferences="Something special")
    response = mock_app.post("/match", json=request.model_dump())
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Couldn't find a match"}
