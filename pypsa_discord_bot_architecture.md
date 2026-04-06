# PyPSA Discord Support Bot — Architecture & Deployment Guide

> **Author:** OpenEnergyTransition Engineering  
> **Role:** Senior DevOps & AI Solutions Architect Advisory  
> **Constraint:** 100% free, open-source, zero ongoing cost

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [The Definitive Tech Stack](#2-the-definitive-tech-stack)
3. [System Architecture Diagram](#3-system-architecture-diagram)
4. [Zero-Cost Deployment Strategy](#4-zero-cost-deployment-strategy)
5. [Groq Free Tier — Know Your Limits](#5-groq-free-tier--know-your-limits)
6. [Architecture Blind Spots](#6-architecture-blind-spots)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Key Code Snippets](#8-key-code-snippets)

---

## 1. Project Overview

A Discord support bot for the PyPSA (Python for Power System Analysis) open-source ecosystem. Users ask troubleshooting, installation, and modeling questions. The system uses a **highly optimized RAG (Retrieval-Augmented Generation) pipeline** rather than a fully autonomous agent to keep latency low and minimize compute overhead.

### RAG Workflow

1. **Ingestion** — Scrape PyPSA docs, PyPSA-Eur docs, solver docs, and GitHub issues
2. **Processing** — Code-aware chunking with rich metadata tagging (`source`, `library`, etc.)
3. **Querying** — Embed user query → retrieve relevant chunks → generate answer via LLM

---

## 2. The Definitive Tech Stack

| Layer | Tool | Justification |
|---|---|---|
| **LLM** | Groq API — `Qwen2.5-Coder-7B-Instruct` | Best code understanding at 7B, ~800 tokens/sec, free tier |
| **Embeddings** | `nomic-embed-text v1.5` via sentence-transformers | 8k context window, Apache 2.0, matches OpenAI quality on code |
| **Vector DB** | Qdrant (Docker) | Payload filtering, on-disk persistence, REST API |
| **Orchestration** | Haystack 2.x | Explicit pipelines, native Qdrant + Groq integrations |
| **Discord** | discord.py | Standard, stable, outbound WebSocket (no inbound ports needed) |
| **Scraping** | crawl4ai + PyGitHub | Clean Markdown from docs, structured issue data |
| **Chunking** | tree-sitter + sliding window | AST-aware, preserves Python code context |
| **Hosting** | Oracle Cloud Always Free ARM VM | 4 vCPU, 24GB RAM, truly always-on, no credit card surprises |
| **Re-indexing** | GitHub Actions cron | Free, 2,000 min/month, sufficient for nightly incremental jobs |

### Why These Choices Over Alternatives

**Groq over self-hosted Ollama:** Groq's free tier runs open-weight models (Qwen, Llama) on LPU hardware at ~800 tokens/sec. Self-hosting a 7B model requires a reliable GPU — difficult to get for free. Groq eliminates this dependency entirely with no closed-model risk.

**nomic-embed-text over all-MiniLM:** MiniLM's 512-token limit will truncate GitHub issue chunks. nomic-embed-text's 8192-token window handles long issues intact. CPU inference is ~50ms per query — not a bottleneck.

**Qdrant over ChromaDB/FAISS:** ChromaDB has persistence reliability issues under concurrent load. FAISS lacks native metadata filtering. Qdrant supports payload filtering at query time (e.g., `filter: {library: "pypsa-eur", source: "github_issue"}`), critical for precision retrieval.

**Haystack 2.x over LangChain:** LangChain's abstraction layers add latency and its changelogs introduce breaking changes frequently. Haystack defines ingestion and query pipelines as explicit, inspectable DAGs — far easier to debug in production.

**tree-sitter over naive chunking:** Naive character/token splitting breaks Python code across function boundaries. tree-sitter splits at the AST level (function definitions, class boundaries, docstrings), keeping `network.add_bus(...)` examples with their surrounding explanation intact.

---

## 3. System Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Discord Server                     │
│              (user asks a question)                  │
└─────────────────────┬───────────────────────────────┘
                      │ discord.py (WebSocket, outbound)
┌─────────────────────▼───────────────────────────────┐
│              Oracle Cloud Free VM                    │
│                 4 ARM CPU / 24GB RAM                 │
│                                                      │
│  ┌─────────────┐    ┌──────────────┐                 │
│  │  discord.py │───▶│ Haystack 2.x │                 │
│  │     bot     │    │   pipeline   │                 │
│  └─────────────┘    └──────┬───────┘                 │
│                            │                         │
│                     ┌──────▼───────┐                 │
│                     │    Qdrant    │                 │
│                     │  (Docker)    │                 │
│                     └─────────────┘                 │
└─────────────────────┬───────────────────────────────┘
                      │ HTTPS (outbound only)
        ┌─────────────▼──────────────┐
        │      Groq Free API         │
        │  Qwen2.5-Coder-7B-Instruct │
        │   ~800 tokens/sec, free    │
        └────────────────────────────┘
```

### Ingestion Pipeline (GitHub Actions, nightly)

```
crawl4ai (docs) ──┐
                  ├──▶ tree-sitter chunker ──▶ nomic embedder ──▶ Qdrant
PyGitHub (issues) ┘         + metadata tags
```

---

## 4. Zero-Cost Deployment Strategy

### Oracle Cloud Always Free VM (Primary Hosting)

Oracle's Always Free tier is the strongest zero-cost compute option available:

- **4 ARM Ampere CPUs, 24GB RAM** — enough for Qdrant, the bot process, and embedding inference
- **200GB block storage** — persistent Qdrant index survives reboots
- **Truly always-on** — not a trial, no expiry, no credit card surprises
- **Outbound-only networking** — discord.py connects outbound to Discord's WebSocket API; no inbound ports required for the bot

### docker-compose.yml (Full Production Stack)

```yaml
version: "3.9"
services:
  qdrant:
    image: qdrant/qdrant
    restart: always
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage

  bot:
    build: .
    restart: always
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - QDRANT_HOST=qdrant
    depends_on:
      - qdrant
```

Both services restart automatically on crash or VM reboot. This is your entire production infrastructure in one file.

### GitHub Actions (Nightly Re-indexing)

```yaml
# .github/workflows/reindex.yml
on:
  schedule:
    - cron: '0 2 * * *'   # 2am UTC nightly
jobs:
  reindex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: python ingestion/incremental_update.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
```

Free 2,000 minutes/month — more than sufficient for nightly incremental indexing.

---

## 5. Groq Free Tier — Know Your Limits

| Model | Requests/day | Tokens/min | Tokens/day |
|---|---|---|---|
| Qwen2.5-Coder-7B | 14,400 | 6,000 | 500,000 |

**The one to watch:** 6,000 tokens/minute. If multiple users ask questions simultaneously, each consuming ~1,500 tokens (context + answer), you can handle ~4 concurrent requests per minute before hitting the rate limit.

**Mitigation:** Implement a simple async queue in discord.py with a 15-second cooldown between Groq calls during high traffic. For a niche technical community this will rarely trigger, but build it in from day one.

---

## 6. Architecture Blind Spots

These are the failure points most likely to affect you in production, ranked by likelihood.

### 1. Query-Document Mismatch (Core RAG Failure Mode)

Users ask questions in conversational language; your chunks are dense technical documentation. The embedding distance between "why does my network throw an infeasible error" and the relevant docs page is large.

**Fix — HyDE (Hypothetical Document Embeddings):** Before retrieving, have the LLM generate a hypothetical answer to the question, then embed *that* for retrieval. The hypothetical answer is lexically closer to your doc chunks than the original question.

### 2. GitHub Issue Noise

Closed issues labeled `wontfix`, Dependabot updates, stale-bot closures, and duplicate reports will pollute your corpus with low-signal content.

**Fix:** Filter at ingestion time:
- Skip issues with zero human comments
- Skip issues closed as duplicates (check label)
- Use `reactions` count as a quality signal — weight high-reaction issues more heavily

### 3. Thread Context Window Mismanagement

Discord threads can grow long. Naively concatenating the last N messages blows your token budget and dilutes retrieval quality.

**Fix:** When thread length exceeds 4 turns, run a summarization step first: `summary + latest_message` becomes your retrieval query. Include the full thread only in the generation prompt after retrieval.

### 4. Solver-Specific Knowledge Gaps

PyPSA users frequently ask about GLPK, HiGHS, and Gurobi solver errors (`infeasible model`, `numerical instability`). These error messages are **not** in PyPSA's official docs — they live in GitHub issue comments and community forums.

**Fix:** Extend ingestion to include:
- PyPSA Google Group archive
- PyPSA-Eur GitHub Discussions
- Solver-specific issue comments (filter by solver name in metadata)

### 5. Stale Index Problem

PyPSA-Eur moves fast. A 3-month-old index will confidently answer questions about deprecated API patterns.

**Fix:** Nightly incremental updates using `updated_at` timestamps and ETags — only re-index content changed since the last run. Never do a full re-ingestion nightly; it's too slow and will miss the window.

### 6. No Confidence Signal to the User

A bot that answers confidently when retrieval quality is poor will erode trust fast.

**Fix:** Qdrant returns cosine similarity scores natively. If all top-k results score below ~0.72, the bot should say: *"I'm not confident I have relevant information for this — here's my best attempt, but please check the docs directly."*

### 7. Cold Start on First Deploy

Ingesting all PyPSA docs + PyPSA-Eur docs + 2+ years of GitHub issues will take hours. A crash mid-ingestion should not restart from zero.

**Fix:** Checkpoint progress in a SQLite table (`url → ingested_at`). On restart, skip already-indexed URLs.

---

## 7. Implementation Roadmap

### Week 1 — Infrastructure
- Provision Oracle Cloud Always Free ARM VM (Ubuntu 22.04)
- Install Docker + Docker Compose
- Deploy Qdrant, verify with health-check curl
- Set up VM auto-restart: `systemctl enable docker`

### Week 2 — Ingestion Pipeline
- Build crawl4ai scrapers for PyPSA + PyPSA-Eur docs
- Build PyGitHub ingestion for issues (filtered: no bots, no duplicates, min 1 human comment)
- Implement tree-sitter chunking + metadata tagging schema
- Index full corpus into Qdrant
- **Validate manually**: run 10 representative test queries, inspect retrieved chunks

### Week 3 — Bot & RAG Pipeline
- Build Haystack 2.x query pipeline (embedder → retriever → prompt builder → Groq)
- Wire discord.py `on_message` handler to pipeline
- Implement thread context summarization (>4 turns)
- Add HyDE for improved retrieval quality
- Add async rate-limit queue for Groq (15s cooldown under burst)

### Week 4 — Hardening & Launch
- Add retrieval confidence threshold message
- Set up GitHub Actions nightly incremental re-indexing
- Add structured logging: log query, top retrieval scores, and response (feedback loop)
- Deploy via docker-compose
- Announce in PyPSA community channels

---

## 8. Key Code Snippets

### Embeddings (CPU, loaded once at startup)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "nomic-ai/nomic-embed-text-v1.5",
    trust_remote_code=True
)
# ~50ms per query on ARM CPU — not a bottleneck
embedding = model.encode("your query here")
```

### Haystack Query Pipeline

```python
from haystack import Pipeline
from haystack_integrations.components.generators.groq import GroqChatGenerator
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

query_pipeline = Pipeline()
query_pipeline.add_component("embedder", embedder)
query_pipeline.add_component(
    "retriever",
    QdrantEmbeddingRetriever(document_store=store, top_k=5)
)
query_pipeline.add_component("prompt_builder", prompt_builder)
query_pipeline.add_component(
    "llm",
    GroqChatGenerator(model="qwen-qwen2.5-coder-7b-instruct")
)

query_pipeline.connect("embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever.documents", "prompt_builder.documents")
query_pipeline.connect("prompt_builder.prompt", "llm.messages")
```

### Retrieval Confidence Check

```python
CONFIDENCE_THRESHOLD = 0.72

results = retriever.run(query_embedding=embedding)
top_scores = [doc.score for doc in results["documents"]]

if max(top_scores) < CONFIDENCE_THRESHOLD:
    await message.reply(
        "⚠️ I'm not confident I have relevant information for this. "
        "Here's my best attempt, but please verify against the docs directly.\n\n"
        + generate_answer(results)
    )
else:
    await message.reply(generate_answer(results))
```

### GitHub Issue Ingestion Filter

```python
def is_quality_issue(issue) -> bool:
    if issue.user.type == "Bot":
        return False
    if any(label.name in ["duplicate", "wontfix", "invalid"] for label in issue.labels):
        return False
    human_comments = [c for c in issue.get_comments() if c.user.type != "Bot"]
    if len(human_comments) == 0:
        return False
    return True
```

### Async Rate-Limit Queue (discord.py)

```python
import asyncio

groq_queue = asyncio.Queue()
COOLDOWN_SECONDS = 15

async def groq_worker():
    while True:
        message, query = await groq_queue.get()
        response = await run_rag_pipeline(query)
        await message.reply(response)
        await asyncio.Sleep(COOLDOWN_SECONDS)
        groq_queue.task_done()

@bot.event
async def on_ready():
    bot.loop.create_task(groq_worker())

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if is_support_channel(message.channel):
        await groq_queue.put((message, message.content))
```

---

## Summary

The system has exactly **two external dependencies**: Discord and Groq. Both are free, both use open-weight models, and both have clear, predictable limits. Everything else — Qdrant, the bot process, embedding inference — runs on hardware you control via Oracle Cloud's Always Free tier. This is as clean and reliable as a zero-cost production system gets.

---

*Generated with architectural guidance from Senior DevOps & AI Solutions Architect review.*
