from unittest.mock import patch

import pytest

from app.utils import find_potential_match, create_chat_for_matched_users
from tests.mocked_data import USER1, USER2, USER3, CHAT_ID, USERS_EMBEDDINGS, QUERY_EMBEDDINGS


@pytest.fixture
def mock_state_manager():
    with patch("app.utils.state_manager") as mock:
        mock.get_users.return_value = {
            USER1.id: USER1,
            USER2.id: USER2,
            USER3.id: USER3,
        }
        mock.get_user.return_value = USER3
        mock.get_users_embedings.return_value = USERS_EMBEDDINGS

        yield mock


@pytest.mark.asyncio
async def test_find_potential_matches_mock_semantic_similarity(mock_settings, mock_state_manager):
    mock_settings.mock_semantic_similarity = True

    users = mock_state_manager.get_users()
    match = await find_potential_match(USER1.id, "the queen", users)

    assert match is not None
    assert match["match_id"] in [USER2.id, USER3.id]

    match = await find_potential_match(USER1.id, "coffee maker", users)
    assert match is None


@pytest.mark.asyncio
async def test_find_potential_matches_semantic_similarity(mock_settings, mock_state_manager):
    mock_settings.mock_semantic_similarity = False
    users = mock_state_manager.get_users()

    with patch("app.services.embeddings_client.embeddings_client.get_embeddings", return_value=QUERY_EMBEDDINGS):
        match = await find_potential_match(USER1.id, "the queen", users)
        assert match is not None
        assert match["match_id"] in [USER2.id, USER3.id]
    
    with patch("app.services.embeddings_client.embeddings_client.get_embeddings", return_value=None):
        match = await find_potential_match(USER1.id, "coffee maker", users)
        assert match is None


def test_create_chat_for_matched_users(mock_state_manager):
    mock_state_manager.get_chat_id_from_matched_pairs.return_value = None
    chat_id = create_chat_for_matched_users(USER1.id, USER2.id)
    
    assert chat_id is not None
    mock_state_manager.set_matched_pairs.assert_called_once_with(USER1.id, USER2.id, chat_id)
    


def test_create_chat_for_matched_users_existing(mock_state_manager):
    mock_state_manager.get_chat_id_from_matched_pairs.return_value = CHAT_ID
    chat_id = create_chat_for_matched_users(USER1.id, USER2.id)
    
    assert chat_id == CHAT_ID
    mock_state_manager.set_matched_pairs.assert_not_called()
