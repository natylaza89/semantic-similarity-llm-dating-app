from fastapi import WebSocket

from app.models.user import User
from app.custom_types import UserID, Users, ChatID, ActiveChat, ActiveChats, MatchedPairs, UsersEmbeddings
from app.config import settings
from app.services.embeddings_client import embeddings_client
from app.services.llm_client import llm_client


class StateManager:
    def __init__(self) -> None:
        self._users: Users = {}
        self._active_chats: ActiveChats = {}
        self._matched_pairs: MatchedPairs = {}
        self._user_embeddings: UsersEmbeddings = {}

    def get_users(self) -> Users:
        return self._users

    async def set_user(self, user_id: UserID, user: User) -> None:
        self._users[user_id] = user
        if not settings.mock_semantic_similarity:
            # TODO: can I mock somehow the LLM response?!
            extracted_keywords_task = await llm_client.get_response(user_input=user.description)
            self.set_user_embeddings(
                user.id,
                embedding=embeddings_client.get_embeddings(text=",".join(extracted_keywords_task.text) if extracted_keywords_task else user.description)
            )

    def get_user(self, user_id: UserID) -> User | None:
        return self._users.get(user_id)

    def get_chat_id_from_matched_pairs(self, user_id: UserID, match_id: UserID) -> ChatID | None:
        return self._matched_pairs.get((user_id,match_id)) or  self._matched_pairs.get((match_id, user_id))

    def get_all_matched_pairs(self) -> MatchedPairs:
        return self._matched_pairs

    def set_matched_pairs(self, user_id: UserID, match_id: UserID, chat_id: ChatID) -> None:
        self._matched_pairs[(user_id, match_id)] = chat_id

    def get_active_chat(self, chat_id: ChatID) -> ActiveChat:
        return self._active_chats[chat_id]

    def set_active_chats(self, chat_id: ChatID, websocket: WebSocket) -> None:
        if chat_id not in self._active_chats:
            self._active_chats[chat_id] = []
        self._active_chats[chat_id].append(websocket)

    def delete_chat_from_active_chats(self, chat_id_to_delete: ChatID, websocket: WebSocket) -> None:
        self._active_chats[chat_id_to_delete].remove(websocket)
        if not self._active_chats[chat_id_to_delete]:
            del self._active_chats[chat_id_to_delete]
            # Remove the chat_id from matched_pairs
            self._matched_pairs = {
                matched_pair: chat_id
                for matched_pair,chat_id in self._matched_pairs.items()
                if chat_id != chat_id_to_delete
            }

    def get_users_embedings(self):
        return self._user_embeddings

    def get_user_embeddings(self, user_id: UserID):
        return self._user_embeddings[user_id]

    def set_user_embeddings(self, user_id: UserID, embedding):
        self._user_embeddings[user_id] = embedding


state_manager = StateManager()
