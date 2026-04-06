"""AST-aware chunking for Python files; sliding-window for everything else."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import TYPE_CHECKING

from pypsa_bot.ingestion.metadata import ChunkMetadata
from pypsa_bot.utils.logging import logger

if TYPE_CHECKING:
    from pypsa_bot.ingestion.scrapers.docs_scraper import ScrapedDocument


# ---------------------------------------------------------------------------
# Tree-sitter setup (lazy-loaded so import errors don't break everything else)
# ---------------------------------------------------------------------------

_ts_parser = None
_ts_available = False


def _get_ts_parser():
    global _ts_parser, _ts_available
    if _ts_parser is not None:
        return _ts_parser
    try:
        import tree_sitter_python as tspython
        from tree_sitter import Language, Parser

        PY_LANGUAGE = Language(tspython.language())
        _ts_parser = Parser(PY_LANGUAGE)
        _ts_available = True
        return _ts_parser
    except Exception as exc:
        logger.warning("tree-sitter not available, falling back to sliding window: %s", exc)
        _ts_available = False
        return None


# ---------------------------------------------------------------------------
# Sliding-window chunker
# ---------------------------------------------------------------------------

def _sliding_window(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks, preferring paragraph/sentence breaks."""
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to break at a paragraph boundary
        break_pos = text.rfind("\n\n", start, end)
        if break_pos == -1 or break_pos <= start:
            # Fall back to sentence boundary
            break_pos = max(
                text.rfind(". ", start, end),
                text.rfind(".\n", start, end),
            )
        if break_pos == -1 or break_pos <= start:
            # Last resort: hard split
            break_pos = end

        chunk = text[start : break_pos + 1].strip()
        if chunk:
            chunks.append(chunk)
        start = break_pos + 1 - overlap

    return [c for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# AST-aware Python chunker
# ---------------------------------------------------------------------------

_TOP_LEVEL_TYPES = {"function_definition", "class_definition", "decorated_definition"}


def _extract_ts_chunks(text: str) -> list[str] | None:
    """Use tree-sitter to split Python source at function/class boundaries.

    Returns None if tree-sitter is unavailable or parsing fails.
    """
    parser = _get_ts_parser()
    if parser is None:
        return None

    try:
        tree = parser.parse(text.encode("utf-8"))
        root = tree.root_node

        chunks: list[str] = []
        last_end = 0
        lines = text.splitlines(keepends=True)

        def byte_offset(line: int, col: int) -> int:
            offset = sum(len(lines[i]) for i in range(min(line, len(lines))))
            offset += col
            return offset

        for node in root.children:
            if node.type in _TOP_LEVEL_TYPES:
                # Include any preamble before the first top-level node
                start_byte = node.start_byte
                if last_end < start_byte:
                    preamble = text[last_end:start_byte].strip()
                    if preamble:
                        chunks.append(preamble)
                chunk_text = text[start_byte : node.end_byte].strip()
                if chunk_text:
                    chunks.append(chunk_text)
                last_end = node.end_byte

        # Remainder (e.g. module-level statements after last definition)
        remainder = text[last_end:].strip()
        if remainder:
            chunks.append(remainder)

        return chunks if chunks else None
    except Exception as exc:
        logger.debug("tree-sitter parse error: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_documents(
    documents: list[ScrapedDocument],
    chunk_size: int = 2000,
    overlap: int = 200,
) -> list[ScrapedDocument]:
    """Chunk a list of ScrapedDocuments into smaller pieces.

    Python files use AST-aware splitting; all other content uses sliding window.

    Args:
        documents: Raw documents to chunk.
        chunk_size: Target maximum characters per chunk for sliding window.
        overlap: Overlap characters between consecutive sliding-window chunks.

    Returns:
        Flat list of chunked ScrapedDocuments with updated metadata.
    """
    from pypsa_bot.ingestion.scrapers.docs_scraper import ScrapedDocument  # avoid circular

    result: list[ScrapedDocument] = []

    for doc in documents:
        text = doc.content.strip()
        if not text:
            continue

        if doc.metadata.content_type == "python":
            raw_chunks = _extract_ts_chunks(text)
            if not raw_chunks:
                # Fall back to sliding window
                raw_chunks = _sliding_window(text, chunk_size, overlap)
        else:
            raw_chunks = _sliding_window(text, chunk_size, overlap)

        total = len(raw_chunks)
        for idx, chunk_text in enumerate(raw_chunks):
            new_meta = deepcopy(doc.metadata)
            new_meta = ChunkMetadata(
                source=new_meta.source,
                library=new_meta.library,
                content_type=new_meta.content_type,
                url=new_meta.url,
                title=new_meta.title,
                chunk_index=idx,
                total_chunks=total,
                updated_at=new_meta.updated_at,
                reactions=new_meta.reactions,
                issue_number=new_meta.issue_number,
            )
            result.append(ScrapedDocument(content=chunk_text, metadata=new_meta))

    return result
