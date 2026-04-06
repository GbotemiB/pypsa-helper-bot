"""Metadata schema for ingested document chunks."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Literal


@dataclass
class ChunkMetadata:
    """Metadata attached to each chunk in the vector store."""

    source: Literal["docs", "github_issue", "github_pr", "source_code", "config"]
    library: Literal["pypsa", "pypsa-eur", "pypsa-earth"]
    content_type: Literal["markdown", "rst", "python", "yaml", "text"]
    url: str = ""
    title: str = ""
    chunk_index: int = 0
    total_chunks: int = 1
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reactions: int = 0
    issue_number: int | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}
