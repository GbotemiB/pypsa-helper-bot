"""Centralized configuration for the PyPSA Helper Bot."""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""

    # --- Required secrets ---
    discord_token: str = field(
        default_factory=lambda: os.environ.get("DISCORD_TOKEN", "")
    )
    groq_api_key: str = field(
        default_factory=lambda: os.environ.get("GROQ_API_KEY", "")
    )
    github_token: str = field(
        default_factory=lambda: os.environ.get("GITHUB_TOKEN", "")
    )

    # --- Qdrant ---
    qdrant_host: str = field(
        default_factory=lambda: os.environ.get("QDRANT_HOST", "localhost")
    )
    qdrant_port: int = field(
        default_factory=lambda: int(os.environ.get("QDRANT_PORT", "6333"))
    )
    qdrant_collection: str = "pypsa_docs"

    # --- LLM ---
    groq_model_primary: str = "qwen-qwen2.5-coder-7b-instruct"
    groq_model_fallback: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    llm_temperature: float = 0.3

    # --- Embeddings ---
    embedding_model: str = "nomic-ai/nomic-embed-text-v1.5"
    embedding_dimension: int = 768

    # --- RAG ---
    retriever_top_k: int = 5
    confidence_threshold: float = 0.72

    # --- Rate limiting ---
    groq_cooldown_seconds: int = 15

    # --- Ingestion ---
    chunk_size: int = 2000
    chunk_overlap: int = 200
    checkpoint_db: str = "ingestion_checkpoint.db"

    # --- Repositories to index ---
    target_repos: dict = field(default_factory=lambda: {
        "pypsa": {
            "github": "PyPSA/pypsa",
            "docs_url": "https://pypsa.readthedocs.io/en/latest/",
        },
        "pypsa-eur": {
            "github": "PyPSA/pypsa-eur",
            "docs_url": "https://pypsa-eur.readthedocs.io/en/latest/",
        },
        "pypsa-earth": {
            "github": "pypsa-meets-earth/pypsa-earth",
            "docs_url": "https://pypsa-earth.readthedocs.io/en/latest/",
        },
    })

    def validate(self, require_discord: bool = True, require_groq: bool = True):
        """Validate that required config values are set."""
        missing = []
        if require_discord and not self.discord_token:
            missing.append("DISCORD_TOKEN")
        if require_groq and not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        if not self.github_token:
            missing.append("GITHUB_TOKEN")
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Set them in your .env file or environment."
            )


# Singleton instance
config = Config()
