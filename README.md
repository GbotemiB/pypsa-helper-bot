# PyPSA Discord Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)
[![LangChain](https://img.shields.io/badge/LangChain-b541d4.svg)](https://www.langchain.com/)

An AI-powered Discord bot designed to provide intelligent, context-aware support for the PyPSA (Python for Power System Analysis) community.


---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works: The RAG Architecture](#how-it-works-the-rag-architecture)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Building the Knowledge Base](#building-the-knowledge-base)
  - [Running the Bot](#running-the-bot)
- [Deployment](#deployment)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

## Overview

The PyPSA ecosystem is powerful and extensive, but its knowledge is distributed across multiple sources: documentation, source code, configuration files, and thousands of historical GitHub issues and discussions. This creates a high barrier to entry for newcomers and a repetitive support load for experienced developers.

This bot aims to solve that problem by acting as a centralized, AI-driven knowledge hub. It listens for questions on Discord, understands them, and provides answers grounded in the project's own data.

## Features

- **Conversational Q&A:** Answers natural language questions when mentioned in a Discord channel.
- **Multi-Source Knowledge:** Ingests and learns from:
  - The `pypsa`, `pypsa-eur`, and `pypsa-earth` GitHub repositories.
  - Documentation files (`.rst`).
  - Python source code (`.py`).
  - Configuration files (`.yaml`).
  - Historical GitHub Issues and Pull Requests.
- **Grounded Answers:** Uses a Retrieval-Augmented Generation (RAG) architecture to ensure answers are based on factual, retrieved context, preventing AI "hallucination."
- **Source Citing:** Includes references to the source documents in its answers, so users can verify information and explore further.

## How It Works: The RAG Architecture

The bot's intelligence is built on a two-stage process:

1.  **Ingestion (Offline):** The `ingest.py` script performs a "learning" phase. It clones the target repositories, loads all specified documents, splits them into manageable chunks, and uses the Google Gemini API to create numerical representations (embeddings) of each chunk. These embeddings are stored in a local FAISS vector database. This database acts as the bot's "long-term memory."

2.  **Inference (Live):** When the `bot.py` script is running:
    - A user mentions the bot with a question.
    - The bot converts the question into an embedding and uses the FAISS index to find the most semantically similar chunks of text from its memory (the "retrieval" step).
    - It then constructs a prompt containing the user's question and the retrieved context.
    - This combined prompt is sent to the Gemini LLM with the instruction to answer the question using *only* the provided context (the "augmented generation" step).

This RAG pipeline ensures that the bot is both knowledgeable and accurate.

## Setup and Installation

### Prerequisites

- Python 3.10+
- A Discord Bot Application
- API Keys for:
  - Discord
  - Google (for the Gemini API)
  - GitHub (a Personal Access Token for API access)

### Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/GbotemiB/pypsa-helper-bot.git
    cd pypsa-helper-bot
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    - Copy the example `.env.example` file to a new file named `.env`.
    - Open `.env` and fill in your secret keys and tokens.
    ```env
    # .env
    DISCORD_BOT_TOKEN="Your_Discord_Bot_Token"
    GOOGLE_API_KEY="Your_Google_API_Key"
    GITHUB_ACCESS_TOKEN="ghp_YourGitHubPersonalAccessToken"
    ```

### Building the Knowledge Base

Before running the bot for the first time, you must build its knowledge base. This process can take a significant amount of time and will consume API credits.
```bash
python ingest.py
```

### Running the bot


```bash
python bot.py
```

If set up correctly, you will see a confirmation message in your terminal that the bot has connected to Discord.

Your bot should now be online and ready to answer questions in the Discord server you added it to.

## Deployment

For a 24/7 production environment, the bot should be deployed to a cloud server.

*   **Recommended Approach:** A small Virtual Private Server (VPS) from a provider like DigitalOcean, Linode, or Hetzner (2 vCPU, 4GB RAM is a good starting point). This provides a persistent filesystem which is ideal for hosting the FAISS index.
*   **Advanced Approach:** A hybrid model using an HPC cluster (like ZIB) to run the intensive `ingest.py` script and then transferring the resulting index to a cheap VPS for the live `bot.py` service.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contributing
Contributions are welcome! If you have ideas for new features, improvements to the knowledge ingestion, or bug fixes, please feel free to open an issue or submit a pull request.
- Fork the repository.
- Create a new branch (git checkout -b feature/your-feature-name).
- Make your changes.
- Commit your changes (git commit -am 'Add some feature').
- Push to the branch (git push origin feature/your-feature-name).
- Create a new Pull Request.

## Acknowledgments

*   The [PyPSA Community](https://pypsa.org/) and [PyPSA-Meets-Earth Initiative](https://github.com/pypsa-meets-earth/pypsa-earth) for building an incredible open-source ecosystem.
*   [LangChain](https://www.langchain.com/) for providing the powerful framework that makes this possible.
*   [discord.py](https://github.com/Rapptz/discord.py) for the robust Discord API wrapper.
*   [Google Gemini](https://ai.google.dev/) for the powerful language models.
*   [FAISS](https://faiss.ai/) for the efficient similarity search library.