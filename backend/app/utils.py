import logging
import random
import uuid
from typing import Optional

import numpy as np

from app.config import settings
from app.services.state_manager import state_manager, StateManager
from app.custom_types import UserID, Users, ChatID, PotentialMatch, Embedding, UsersEmbeddings, BestMatchScore, SimilarityScore
from app.services.embeddings_client import embeddings_client
from app.services.llm_client import llm_client


_logger = logging.getLogger(__name__)


async def find_potential_match(user_id: UserID, preferences: str, users: Users) -> PotentialMatch:
    if settings.mock_semantic_similarity:
        return __mocked_semantic_similarity_potential_match(user_id, preferences, users)
    return await __semantic_similarity_potential_match(user_id, preferences)


def __get_user_match_info(state_manager: StateManager, match_id: UserID) -> PotentialMatch:
    user_info = state_manager.get_user(match_id)
    if not user_info:
        return None

    user_metadata = user_info.model_dump()
    user_metadata["match_id"] = match_id
    return user_metadata


def __mocked_semantic_similarity_potential_match(user_id: UserID, preferences: str, users: Users) -> PotentialMatch:
    potential_matches = [
        other_id
        for other_id, other_user in users.items()
        if other_id != user_id and (
                preferences.lower() in other_user.description.lower() or
                other_user.description.lower() in preferences.lower()
        )
    ]

    if not potential_matches:
        return None

    return random.choice([
        __get_user_match_info(state_manager, match_id)
        for match_id in potential_matches
        if __get_user_match_info(state_manager, match_id)
    ])


async def __semantic_similarity_potential_match(user_id: UserID, preferences: str) -> PotentialMatch:
        try:
            user = state_manager.get_user(user_id) 
            if user is None:
                raise ValueError("User is missing")
            
            preferences_extracted_keywords = await llm_client.get_response(user_input=preferences)
            
            query = f"User Description: {user.description}\nPreferences: {preferences_extracted_keywords or preferences}"
            query_embedding = embeddings_client.get_embeddings(query)
            if query_embedding is None:
                raise ValueError("Failed to get query embedding")

            other_embeddings = {
                other_id: other_embedding
                for other_id, other_embedding in state_manager.get_users_embedings().items()
                if other_id != user_id
            }

            best_match_id, similarity = find_best_match(query_embedding, other_embeddings)
            if not best_match_id:
                return None

            _logger.debug(f"Best match user_id: {best_match_id}, similarity: {similarity}")

            return __get_user_match_info(state_manager, best_match_id)
        except Exception as e:
            _logger.error(f"Error finding top match: {e}")
            return None


def cosine_similarity(v1: Embedding, v2: Embedding) -> SimilarityScore:
    """ Calculate the similarity between two embedding vectors """
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def find_best_match(query_embedding: Embedding, other_embeddings: UsersEmbeddings) -> tuple[Optional[UserID], BestMatchScore]:
    best_match_id: Optional[UserID] = None
    best_similarity = -1.0

    for other_id, other_embedding in other_embeddings.items():
        similarity: SimilarityScore = cosine_similarity(query_embedding, other_embedding)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match_id = other_id

    return best_match_id, best_similarity


def create_chat_for_matched_users(user_id: UserID, match_id: UserID) -> ChatID:
    existing_chat_id = (
            state_manager.get_chat_id_from_matched_pairs(user_id, match_id) or
            state_manager.get_chat_id_from_matched_pairs(match_id, user_id)
    )
    if existing_chat_id:
        return existing_chat_id

    chat_id = str(uuid.uuid4())
    state_manager.set_matched_pairs(user_id, match_id, chat_id)
    return chat_id
