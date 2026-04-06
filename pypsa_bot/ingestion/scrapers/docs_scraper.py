"""Docs scraper that reads source files directly from cloned repositories."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import git

from pypsa_bot.config import Config
from pypsa_bot.ingestion.metadata import ChunkMetadata
from pypsa_bot.utils.logging import logger

# Maps library name → (repo_url, glob_patterns_relative_to_repo_root)
REPO_CONFIG: dict[str, dict] = {
    "pypsa": {
        "url": "https://github.com/PyPSA/PyPSA.git",
        "patterns": [
            ("docs/**/*.md", "docs"),
            ("pypsa/**/*.py", "source_code"),
            ("test/**/*.py", "source_code"),
            ("**/*.yml", "config"),
            ("**/*.yaml", "config"),
        ],
    },
    "pypsa-eur": {
        "url": "https://github.com/PyPSA/pypsa-eur.git",
        "patterns": [
            ("doc/**/*.rst", "docs"),
            ("scripts/**/*.py", "source_code"),
            ("**/*.yml", "config"),
            ("**/*.yaml", "config"),
        ],
    },
    "pypsa-earth": {
        "url": "https://github.com/pypsa-meets-earth/pypsa-earth.git",
        "patterns": [
            ("doc/**/*.rst", "docs"),
            ("scripts/**/*.py", "source_code"),
            ("**/*.yml", "config"),
            ("**/*.yaml", "config"),
        ],
    },
}

EXT_TO_CONTENT_TYPE: dict[str, str] = {
    ".md": "markdown",
    ".rst": "rst",
    ".py": "python",
    ".yaml": "yaml",
    ".yml": "yaml",
}


@dataclass
class ScrapedDocument:
    """A raw document scraped from a source before chunking."""

    content: str
    metadata: ChunkMetadata


def _ensure_repo(library: str, cloned_repos_root: Path) -> Path:
    """Clone the repo if it doesn't exist; return path to repo dir."""
    repo_dir = cloned_repos_root / library
    if repo_dir.exists() and (repo_dir / ".git").exists():
        logger.info("Repo %s already cloned at %s", library, repo_dir)
        return repo_dir

    url = REPO_CONFIG[library]["url"]
    logger.info("Cloning %s from %s → %s", library, url, repo_dir)
    git.Repo.clone_from(url, str(repo_dir), depth=1)
    logger.info("Cloned %s successfully", library)
    return repo_dir


def _glob_files(repo_dir: Path, pattern: str) -> Iterable[Path]:
    """Yield files matching a glob pattern inside the repo directory."""
    yield from repo_dir.glob(pattern)


def _read_file(path: Path) -> str | None:
    """Read a file, ignoring encoding errors."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return None


def scrape_docs(config: Config, target_repo: str | None = None) -> list[ScrapedDocument]:
    """Walk cloned repo directories and load documentation/source files.

    Args:
        config: Application configuration (used for cloned_repos path etc.)
        target_repo: If set, only scrape that library (e.g. "pypsa").

    Returns:
        List of ScrapedDocument instances.
    """
    project_root = Path(__file__).resolve().parents[4]
    cloned_repos_root = project_root / "cloned_repos"
    cloned_repos_root.mkdir(parents=True, exist_ok=True)

    libraries = [target_repo] if target_repo else list(REPO_CONFIG.keys())
    documents: list[ScrapedDocument] = []

    for library in libraries:
        if library not in REPO_CONFIG:
            logger.warning("Unknown library %s — skipping", library)
            continue

        repo_dir = _ensure_repo(library, cloned_repos_root)
        seen_paths: set[Path] = set()

        for pattern, source_type in REPO_CONFIG[library]["patterns"]:
            for file_path in _glob_files(repo_dir, pattern):
                if not file_path.is_file():
                    continue
                if file_path in seen_paths:
                    continue
                seen_paths.add(file_path)

                ext = file_path.suffix.lower()
                content_type = EXT_TO_CONTENT_TYPE.get(ext, "text")
                content = _read_file(file_path)
                if not content or not content.strip():
                    continue

                # Build a relative URL-like identifier
                rel_path = file_path.relative_to(repo_dir)
                url = f"file://{library}/{rel_path.as_posix()}"

                metadata = ChunkMetadata(
                    source=source_type,  # type: ignore[arg-type]
                    library=library,  # type: ignore[arg-type]
                    content_type=content_type,  # type: ignore[arg-type]
                    url=url,
                    title=file_path.name,
                )
                documents.append(ScrapedDocument(content=content, metadata=metadata))

        logger.info("Scraped %d files from %s", len(seen_paths), library)

    return documents
