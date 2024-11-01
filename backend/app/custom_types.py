from typing import NamedTuple

from fastapi import WebSocket

from app.models.user import User


UserID = str
ChatID = str
Users = dict[UserID, User]
PotentialMatch = dict | None
ActiveChat = list[WebSocket]
ActiveChats = dict[ChatID, ActiveChat]
MatchedPairs = dict[tuple[UserID,UserID], ChatID]
Embedding = list[float]
UsersEmbeddings = dict[UserID, Embedding]
BestMatchScore = float
SimilarityScore = float


class LlmTasks(NamedTuple):
    TEXT_EXTRACTION: str = "text_extraction"
