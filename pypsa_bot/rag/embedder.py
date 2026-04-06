"""Query embedding using nomic-embed-text."""
from sentence_transformers import SentenceTransformer
from pypsa_bot.config import Config
from pypsa_bot.utils.logging import logger


class QueryEmbedder:
    def __init__(self, config: Config):
        logger.info(f"Loading embedding model: {config.embedding_model}")
        self._model = SentenceTransformer(config.embedding_model, trust_remote_code=True)
        self._dimension = config.embedding_dimension

    def embed(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [e.tolist() for e in self._model.encode(texts)]

    @property
    def dimension(self) -> int:
        return self._dimension
