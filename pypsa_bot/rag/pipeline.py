"""Full RAG query pipeline."""
from dataclasses import dataclass
from pypsa_bot.config import Config
from pypsa_bot.rag.embedder import QueryEmbedder
from pypsa_bot.rag.generator import AnswerGenerator
from pypsa_bot.rag.hyde import HyDEGenerator
from pypsa_bot.rag.retriever import QdrantRetriever, RetrievedDocument
from pypsa_bot.utils.logging import logger


@dataclass
class RAGResult:
    answer: str
    documents: list[RetrievedDocument]
    is_confident: bool
    top_score: float


class RAGPipeline:
    def __init__(self, config: Config):
        logger.info("Initializing RAG pipeline...")
        self._config = config
        self._embedder = QueryEmbedder(config)
        self._hyde = HyDEGenerator(config)
        self._retriever = QdrantRetriever(config, self._embedder)
        self._generator = AnswerGenerator(config)
        self._confidence_threshold = config.confidence_threshold
        logger.info("RAG pipeline ready")

    def query(self, question, library=None, source=None, use_hyde=True):
        logger.info(f"RAG query: '{question[:80]}...'")
        text = self._hyde.generate_hypothetical_answer(question) if use_hyde else question
        embedding = self._embedder.embed(text)
        docs = self._retriever.retrieve(embedding, library=library, source=source)
        top_score = docs[0].score if docs else 0.0
        is_confident = top_score >= self._confidence_threshold
        if not is_confident:
            logger.warning(f"Low confidence: {top_score:.3f} < {self._confidence_threshold}")
        answer = self._generator.generate(question, docs)
        return RAGResult(answer=answer, documents=docs, is_confident=is_confident, top_score=top_score)
