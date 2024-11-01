import logging
from typing import Optional

import cohere

from app.config import settings
from app.custom_types import Embedding

_logger = logging.getLogger(__name__)


class EmbeddingsClient:
    def __init__(self) -> None:
        self._client = cohere.ClientV2(settings.cohere_api_key.get_secret_value())

    def get_embeddings(self, text: str) -> Optional[Embedding]:
        try:
            response = self._client.embed(
                texts=[text],
                input_type="search_query", 
                embedding_types=["float"],
                model="embed-english-v3.0",
                truncate="END"
            )
            embeddings = response.embeddings
            if not embeddings or not hasattr(embeddings, 'float_') or not embeddings.float_:
                _logger.warning("Embeddings value from Cohere has invalid value.")
                return None
            return embeddings.float_[0]
        except Exception as e:
            _logger.error(f"Error getting embedding: {e}")
            return None


embeddings_client = EmbeddingsClient()
