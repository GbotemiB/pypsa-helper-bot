"""Qdrant vector retriever with confidence scoring."""
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from pypsa_bot.config import Config
from pypsa_bot.rag.embedder import QueryEmbedder
from pypsa_bot.utils.logging import logger


@dataclass
class RetrievedDocument:
    content: str
    score: float
    metadata: dict


class QdrantRetriever:
    def __init__(self, config: Config, embedder: QueryEmbedder):
        self._client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
        self._collection = config.qdrant_collection
        self._top_k = config.retriever_top_k
        self._embedder = embedder

    def retrieve(self, query_embedding, top_k=None, library=None, source=None):
        k = top_k or self._top_k
        must = []
        if library:
            must.append(FieldCondition(key="library", match=MatchValue(value=library)))
        if source:
            must.append(FieldCondition(key="source", match=MatchValue(value=source)))
        qf = Filter(must=must) if must else None

        results = self._client.query_points(
            collection_name=self._collection, query=query_embedding,
            query_filter=qf, limit=k, with_payload=True,
        )
        docs = []
        for pt in results.points:
            p = pt.payload or {}
            docs.append(RetrievedDocument(
                content=p.get("content", ""), score=pt.score,
                metadata={k: v for k, v in p.items() if k != "content"},
            ))
        if docs:
            logger.info(f"Retrieved {len(docs)} docs, top score: {docs[0].score:.3f}")
        return docs
