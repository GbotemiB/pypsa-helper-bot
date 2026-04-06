"""SQLite-backed checkpoint for incremental ingestion and crash recovery."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path


class IngestionCheckpoint:
    """Track which URLs have already been ingested.

    Thread-safe for concurrent access within a single process.

    Args:
        db_path: Path to the SQLite database file.
    """

    _CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS ingested_urls (
        url          TEXT PRIMARY KEY,
        etag         TEXT,
        content_hash TEXT,
        ingested_at  TEXT DEFAULT (datetime('now'))
    )
    """

    def __init__(self, db_path: str | Path = "ingestion_checkpoint.db") -> None:
        self._db_path = str(db_path)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(self._CREATE_TABLE)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_ingested(self, url: str) -> bool:
        """Return True if the URL has been marked as ingested."""
        with self._lock:
            cur = self._conn.execute(
                "SELECT 1 FROM ingested_urls WHERE url = ?", (url,)
            )
            return cur.fetchone() is not None

    def mark_ingested(
        self,
        url: str,
        etag: str | None = None,
        content_hash: str | None = None,
    ) -> None:
        """Record a URL as successfully ingested.

        If the URL already exists, update its etag / content_hash.
        """
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO ingested_urls (url, etag, content_hash)
                VALUES (?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    etag = excluded.etag,
                    content_hash = excluded.content_hash,
                    ingested_at = datetime('now')
                """,
                (url, etag, content_hash),
            )
            self._conn.commit()

    def get_ingested_count(self) -> int:
        """Return the total number of ingested URLs."""
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(*) FROM ingested_urls")
            row = cur.fetchone()
            return row[0] if row else 0

    def clear(self) -> None:
        """Remove all checkpoint entries (full re-ingest)."""
        with self._lock:
            self._conn.execute("DELETE FROM ingested_urls")
            self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        with self._lock:
            self._conn.close()

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> IngestionCheckpoint:
        return self

    def __exit__(self, *_) -> None:
        self.close()
