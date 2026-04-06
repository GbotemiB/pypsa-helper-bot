"""Main ingestion orchestrator: scrape → chunk → embed → upsert to Qdrant."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

from pypsa_bot.ingestion.checkpoint import IngestionCheckpoint
from pypsa_bot.ingestion.chunker import chunk_documents
from pypsa_bot.ingestion.scrapers.docs_scraper import scrape_docs
from pypsa_bot.ingestion.scrapers.github_scraper import scrape_github_issues
from pypsa_bot.utils.logging import logger

if TYPE_CHECKING:
    from pypsa_bot.config import Config

BATCH_SIZE = 64


def _ensure_collection(client: QdrantClient, collection: str, dimension: int) -> None:
    """Create the Qdrant collection if it doesn't already exist."""
    existing = {c.name for c in client.get_collections().collections}
    if collection not in existing:
        logger.info("Creating Qdrant collection '%s' (dim=%d)", collection, dimension)
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )
    else:
        logger.info("Qdrant collection '%s' already exists", collection)


def run_ingestion(
    config: Config,
    incremental: bool = False,
    target_repo: str | None = None,
) -> None:
    """Run the full ingestion pipeline.

    Steps:
    1. Scrape docs (from cloned repos) + GitHub issues.
    2. Chunk with tree-sitter / sliding window.
    3. Embed with nomic-ai/nomic-embed-text-v1.5 via SentenceTransformer.
    4. Upsert to Qdrant (skipping already-ingested URLs when incremental=True).

    Args:
        config: Application configuration.
        incremental: If True, skip URLs already recorded in the checkpoint DB.
        target_repo: Limit scraping to a single library (e.g. "pypsa").
    """
    logger.info("Starting ingestion — incremental=%s, target_repo=%s", incremental, target_repo)

    # ------------------------------------------------------------------ #
    # 1. Scrape
    # ------------------------------------------------------------------ #
    docs_documents = scrape_docs(config, target_repo=target_repo)
    logger.info("Scraped %d documents from repos", len(docs_documents))

    issue_documents = scrape_github_issues(config, target_repo=target_repo)
    logger.info("Scraped %d GitHub issues", len(issue_documents))

    all_documents = docs_documents + issue_documents

    # ------------------------------------------------------------------ #
    # 2. Chunk
    # ------------------------------------------------------------------ #
    chunked = chunk_documents(
        all_documents,
        chunk_size=config.chunk_size,
        overlap=config.chunk_overlap,
    )
    logger.info("Produced %d chunks after chunking", len(chunked))

    # ------------------------------------------------------------------ #
    # 3. Load model + checkpoint
    # ------------------------------------------------------------------ #
    logger.info("Loading embedding model: %s", config.embedding_model)
    model = SentenceTransformer(
        config.embedding_model,
        trust_remote_code=True,  # required for nomic-embed-text-v1.5
    )

    checkpoint = IngestionCheckpoint(config.checkpoint_db)

    # ------------------------------------------------------------------ #
    # 4. Connect to Qdrant
    # ------------------------------------------------------------------ #
    client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
    _ensure_collection(client, config.qdrant_collection, config.embedding_dimension)

    # ------------------------------------------------------------------ #
    # 5. Embed + upsert in batches
    # ------------------------------------------------------------------ #
    total_upserted = 0
    total_skipped = 0
    batch: list = []

    def _flush_batch(b: list) -> None:
        nonlocal total_upserted
        if not b:
            return
        texts = [item["text"] for item in b]
        vectors = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[i].tolist(),
                payload={**item["meta"], "text": item["text"]},
            )
            for i, item in enumerate(b)
        ]
        client.upsert(collection_name=config.qdrant_collection, points=points)
        for item in b:
            checkpoint.mark_ingested(item["url"])
        total_upserted += len(b)
        logger.debug("Upserted batch of %d points", len(b))

    for doc in chunked:
        url_key = f"{doc.metadata.url}#chunk{doc.metadata.chunk_index}"

        if incremental and checkpoint.is_ingested(url_key):
            total_skipped += 1
            continue

        batch.append(
            {
                "text": doc.content,
                "url": url_key,
                "meta": doc.metadata.to_dict(),
            }
        )

        if len(batch) >= BATCH_SIZE:
            _flush_batch(batch)
            batch = []

    _flush_batch(batch)

    checkpoint.close()
    client.close()

    logger.info(
        "Ingestion complete — upserted=%d, skipped=%d", total_upserted, total_skipped
    )
