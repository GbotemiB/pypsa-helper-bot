# PyPSA Helper Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg)](https://groq.com/)

An AI-powered Discord bot designed to provide intelligent, context-aware support for the [PyPSA](https://pypsa.org/) (Python for Power System Analysis) community.

---

## Table of Contents

- [Project Description](#project-description)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running Locally](#running-locally)
- [Docker Deployment](#docker-deployment)
- [CLI Reference](#cli-reference)
- [Contributing](#contributing)
- [License](#license)

---

## Project Description

The PyPSA ecosystem is powerful and extensive, but its knowledge is spread across multiple sources: documentation, source code, configuration files, and thousands of historical GitHub issues and discussions. This creates a high barrier to entry for newcomers and a repetitive support load for experienced developers.

The PyPSA Helper Bot solves this by acting as a centralized, AI-driven knowledge hub. It listens for questions on Discord, understands them using a Retrieval-Augmented Generation (RAG) pipeline, and provides grounded answers sourced from the project's own data — including the `pypsa`, `pypsa-eur`, and `pypsa-earth` repositories.

---

## Architecture Overview

The bot uses a **HyDE-enhanced RAG pipeline** (Hypothetical Document Embeddings):

```
User question
     │
     ▼
Groq LLM generates a hypothetical answer (HyDE)
     │
     ▼
nomic-embed-text embeds the hypothetical answer
     │
     ▼
Qdrant vector search retrieves relevant context chunks
     │
     ▼
Groq LLM generates the final grounded answer
     │
     ▼
Answer posted to Discord
```

**Why HyDE?** Instead of embedding the raw user question (which may be short or ambiguous), the bot first asks the LLM to generate a hypothetical ideal answer. That answer is then embedded, producing a richer semantic signal for the vector search step — leading to more relevant context retrieval and better final answers.

**Ingestion pipeline:**

```
GitHub repos (pypsa, pypsa-eur, pypsa-earth)
     │
     ▼
tree-sitter (Python AST) + sliding window chunker
     │
     ▼
nomic-embed-text embeds each chunk
     │
     ▼
Stored in Qdrant vector database
```

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Discord | discord.py | Bot framework, event handling, message I/O |
| LLM | Groq (Qwen2.5-Coder-7B, fallback Llama 4 Scout) | HyDE generation and final answer generation |
| Embeddings | nomic-ai/nomic-embed-text-v1.5 (sentence-transformers) | Dense vector embeddings for semantic search |
| Vector DB | Qdrant | Storing and querying document embeddings |
| Chunking | tree-sitter (Python AST) + sliding window | Context-aware document chunking |
| Package mgmt | uv + pyproject.toml | Fast, reproducible dependency management |

---

## Prerequisites

- Python 3.11+
- Docker (for running Qdrant locally or full stack deployment)
- [uv](https://docs.astral.sh/uv/) package manager
- API keys:
  - **Discord** — Bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
  - **Groq** — API key from [console.groq.com](https://console.groq.com)
  - **GitHub** — Personal Access Token for repository API access

---

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/GbotemiB/pypsa-helper-bot.git
   cd pypsa-helper-bot
   ```

2. **Install dependencies with uv:**

   ```bash
   uv sync
   ```

3. **Configure environment variables:**

   ```bash
   cp .env.sample .env
   ```

   Open `.env` and fill in your keys:

   ```env
   DISCORD_TOKEN=your_discord_bot_token
   GROQ_API_KEY=your_groq_api_key
   GITHUB_TOKEN=your_github_personal_access_token
   QDRANT_URL=http://localhost:6333
   ```

---

## Running Locally

Start Qdrant (vector database):

```bash
docker-compose up -d qdrant
```

Ingest PyPSA documentation and source code into the vector database:

```bash
uv run pypsa-bot ingest
```

Start the Discord bot:

```bash
uv run pypsa-bot run
```

The bot will connect to Discord and begin responding to mentions in any channel it has access to.

---

## Docker Deployment

To run both Qdrant and the bot together using Docker Compose:

```bash
docker-compose up -d
```

This starts:
- `qdrant` — vector database on port 6333
- `bot` — the Discord bot (with `restart: always` for auto-recovery)

To run ingestion inside the running bot container:

```bash
docker-compose exec bot pypsa-bot ingest
```

To view logs:

```bash
docker-compose logs -f bot
```

---

## CLI Reference

The `pypsa-bot` command is the main entry point (defined in `pyproject.toml`).

| Command | Description |
|---|---|
| `pypsa-bot run` | Start the Discord bot |
| `pypsa-bot ingest` | Full ingestion of all configured repos |
| `pypsa-bot ingest --incremental` | Only ingest new or updated content |
| `pypsa-bot ingest --repo pypsa` | Ingest a specific repository only |

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit:
   ```bash
   git commit -m "Add your feature description"
   ```
4. Push to your fork and open a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

Please open an issue first for significant changes so the approach can be discussed before implementation.

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
