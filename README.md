# PyPSA Discord Bot# PyPSA Discord Bot



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)[![discord.py](https://img.shields.io/badge/discord-py-blue.svg)](https://github.com/Rapptz/discord.py)

[![LangChain](https://img.shields.io/badge/LangChain-b541d4.svg)](https://www.langchain.com/)[![LangChain](https://img.shields.io/badge/LangChain-b541d4.svg)](https://www.langchain.com/)



An AI-powered Discord bot designed to provide intelligent, context-aware support for the PyPSA (Python for Power System Analysis) community.An AI-powered Discord bot designed to provide intelligent, context-aware support for the PyPSA (Python for Power System Analysis) community.



---

---

## Overview

## Table of Contents

The PyPSA ecosystem is powerful and extensive, but its knowledge is distributed across multiple sources: documentation, source code, configuration files, and thousands of historical GitHub issues and discussions. This creates a high barrier to entry for newcomers and a repetitive support load for experienced developers.

- [Overview](#overview)

This bot aims to solve that problem by acting as a centralized, AI-driven knowledge hub. It listens for questions on Discord, understands them, and provides answers grounded in the project's own data.- [Features](#features)

- [How It Works: The RAG Architecture](#how-it-works-the-rag-architecture)

## Features- [Setup and Installation](#setup-and-installation)

  - [Prerequisites](#prerequisites)

- **Conversational Q&A:** Answers natural language questions when mentioned in a Discord channel.  - [Configuration](#configuration)

- **Multi-Source Knowledge:** Ingests and learns from:  - [Building the Knowledge Base](#building-the-knowledge-base)

  - The `pypsa`, `pypsa-eur`, and `pypsa-earth` GitHub repositories.  - [Running the Bot](#running-the-bot)

  - Documentation files (`.rst`).- [Deployment](#deployment)

  - Python source code (`.py`).- [License](#license)

  - Configuration files (`.yaml`).- [Contributing](#contributing)

  - Historical GitHub Issues and Pull Requests.- [Acknowledgments](#acknowledgments)

- **Grounded Answers:** Uses a Retrieval-Augmented Generation (RAG) architecture to ensure answers are based on factual, retrieved context, preventing AI "hallucination."

- **Source Citing:** Includes references to the source documents in its answers, so users can verify information and explore further.## Overview



## How It Works: The RAG ArchitectureThe PyPSA ecosystem is powerful and extensive, but its knowledge is distributed across multiple sources: documentation, source code, configuration files, and thousands of historical GitHub issues and discussions. This creates a high barrier to entry for newcomers and a repetitive support load for experienced developers.



The bot's intelligence is built on a two-stage process:This bot aims to solve that problem by acting as a centralized, AI-driven knowledge hub. It listens for questions on Discord, understands them, and provides answers grounded in the project's own data.



1.  **Ingestion (Offline):** The `ingest.py` script performs a "learning" phase. It clones the target repositories, loads all specified documents, splits them into manageable chunks, and uses the Google Gemini API to create numerical representations (embeddings) of each chunk. These embeddings are stored in a local FAISS vector database. This database acts as the bot's "long-term memory."## Features



2.  **Inference (Live):** When the `bot.py` script is running:- **Conversational Q&A:** Answers natural language questions when mentioned in a Discord channel.

    - A user mentions the bot with a question.- **Multi-Source Knowledge:** Ingests and learns from:

    - The bot converts the question into an embedding and uses the FAISS index to find the most semantically similar chunks of text from its memory (the "retrieval" step).  - The `pypsa`, `pypsa-eur`, and `pypsa-earth` GitHub repositories.

    - It then constructs a prompt containing the user's question and the retrieved context.  - Documentation files (`.rst`).

    - This combined prompt is sent to the Gemini LLM with the instruction to answer the question using *only* the provided context (the "augmented generation" step).  - Python source code (`.py`).

  - Configuration files (`.yaml`).

This RAG pipeline ensures that the bot is both knowledgeable and accurate.  - Historical GitHub Issues and Pull Requests.

- **Grounded Answers:** Uses a Retrieval-Augmented Generation (RAG) architecture to ensure answers are based on factual, retrieved context, preventing AI "hallucination."

## Setup and Installation- **Source Citing:** Includes references to the source documents in its answers, so users can verify information and explore further.



### Prerequisites## How It Works: The RAG Architecture



- Python 3.11+The bot's intelligence is built on a two-stage process:

- A Discord Bot Application

- API Keys for:1.  **Ingestion (Offline):** The `ingest.py` script performs a "learning" phase. It clones the target repositories, loads all specified documents, splits them into manageable chunks, and uses the Google Gemini API to create numerical representations (embeddings) of each chunk. These embeddings are stored in a local FAISS vector database. This database acts as the bot's "long-term memory."

  - Discord Bot Token

  - Google Gemini API Key2.  **Inference (Live):** When the `bot.py` script is running:

  - GitHub Personal Access Token (for accessing repositories)    - A user mentions the bot with a question.

    - The bot converts the question into an embedding and uses the FAISS index to find the most semantically similar chunks of text from its memory (the "retrieval" step).

### Installation    - It then constructs a prompt containing the user's question and the retrieved context.

    - This combined prompt is sent to the Gemini LLM with the instruction to answer the question using *only* the provided context (the "augmented generation" step).

1.  **Clone the repository:**

    ```bashThis RAG pipeline ensures that the bot is both knowledgeable and accurate.

    git clone https://github.com/GbotemiB/pypsa-helper-bot.git

    cd pypsa-helper-bot## Setup and Installation

    ```

### Prerequisites

2.  **Create a virtual environment and install dependencies:**

    ```bash- Python 3.10+

    python -m venv venv- A Discord Bot Application

    source venv/bin/activate  # On Windows: venv\Scripts\activate- API Keys for:

    pip install -r requirements.txt  - Discord

    ```  - Google (for the Gemini API)

  - GitHub (a Personal Access Token for API access)

3.  **Set up your environment variables:**

    Create a `.env` file in the root directory:### Configuration

    ```env

    DISCORD_BOT_TOKEN="your_discord_bot_token"1.  **Clone the repository:**

    GOOGLE_API_KEY="your_google_api_key"    ```bash

    GITHUB_ACCESS_TOKEN="your_github_token"    git clone https://github.com/GbotemiB/pypsa-helper-bot.git

    ```    cd pypsa-helper-bot

    ```

### Building the Knowledge Base

2.  **Create a virtual environment and install dependencies:**

Before running the bot for the first time, you must build its knowledge base:    ```bash

    python -m venv venv

```bash    source venv/bin/activate  # On Windows: venv\Scripts\activate

python src/ingest.py    pip install -r requirements.txt

```    ```



**Note:** This process can take 30-60 minutes and will consume API credits.3.  **Set up your environment variables:**

    - Copy the example `.env.example` file to a new file named `.env`.

### Running the Bot    - Open `.env` and fill in your secret keys and tokens.

    ```env

```bash    # .env

python src/bot.py    DISCORD_BOT_TOKEN="Your_Discord_Bot_Token"

```    GOOGLE_API_KEY="Your_Google_API_Key"

    GITHUB_ACCESS_TOKEN="ghp_YourGitHubPersonalAccessToken"

Your bot should now be online and ready to answer questions in the Discord server you added it to.    ```



## Automated Knowledge Base Updates### Building the Knowledge Base



The repository includes GitHub Actions workflows for automation:Before running the bot for the first time, you must build its knowledge base. This process can take a significant amount of time and will consume API credits.

```bash

### Daily Reindexing (`.github/workflows/reindex.yml`)python ingest.py

- **Runs:** Daily at 00:00 UTC```

- **Action:** Rebuilds the FAISS knowledge base

- **Storage:** Uploads to GitHub Releases### Running the bot

- **Retention:** Keeps last 7 releases



### Testing (`.github/workflows/test.yml`)```bash

- **Runs:** On push to mainpython bot.py

- **Action:** Verifies setup and dependencies```



### Setup RequiredIf set up correctly, you will see a confirmation message in your terminal that the bot has connected to Discord.



Add these secrets to your GitHub repository (Settings → Secrets → Actions):Your bot should now be online and ready to answer questions in the Discord server you added it to.

- `GOOGLE_API_KEY` - Your Google Gemini API key

- `GITHUB_TOKEN` - Automatically provided by GitHub Actions## Deployment



## Project StructureThis bot is designed to be deployed on **Azure Container Instances** with automatic daily knowledge base updates via **GitHub Actions**.



```### Quick Deploy to Azure

pypsa-helper-bot/

├── src/See the complete guide: **[docs/AZURE_SETUP.md](docs/AZURE_SETUP.md)**

│   ├── bot.py          # Main Discord bot

│   ├── ingest.py       # Knowledge base builder**Quick overview:**

│   └── storage.py      # GitHub Releases integration1. Sign up for Azure (students get $100 credit, no credit card needed)

├── .github/workflows/2. Create resource group and container registry

│   ├── reindex.yml     # Daily knowledge base update3. Set up GitHub secrets for automated deployment

│   └── test.yml        # Setup verification4. Push to main branch → Auto-deploy via GitHub Actions

├── requirements.txt    # Python dependencies

├── Dockerfile         # Container configuration### Features

└── README.md          # This file

```✅ **Automated Daily Reindexing** - GitHub Actions updates knowledge base at 00:00 UTC  

✅ **Hot-Reload** - Bot detects and loads new index without downtime  

## Deployment✅ **Student-Friendly** - Azure for Students ($100 credit, no CC required)  

✅ **Zero Setup Storage** - Uses GitHub Releases for index storage  

This bot can be deployed to any platform that supports Docker containers:✅ **Auto-Deploy** - Push to main = automatic deployment  



- **Docker Hub** - Public container registry### Architecture

- **Azure Container Instances** - Azure's container service

- **Railway.app** - Simple deployment with GitHub integration```

- **Self-hosted** - Run on your own serverGitHub Actions (Daily 00:00 UTC)

  ↓ Run ingest.py

Use the provided `Dockerfile` for containerization.  ↓ Build FAISS Index

  ↓ Upload to GitHub Releases

## License  

Azure Container Instances

Distributed under the MIT License. See `LICENSE` for more information.  ↓ Download latest index

  ↓ Hot-reload every 5 minutes

## Contributing  ↓ Serve Discord requests

```

Contributions are welcome! If you have ideas for new features, improvements to the knowledge ingestion, or bug fixes, please feel free to open an issue or submit a pull request.

For detailed instructions, see:

1. Fork the repository- 🎓 **[Azure Setup Guide](docs/AZURE_SETUP.md)** ← START HERE

2. Create a feature branch (`git checkout -b feature/your-feature`)- � [Installation Guide](docs/INSTALLATION.md)

3. Commit your changes (`git commit -am 'Add feature'`)- 🧪 [Testing Guide](docs/TESTING.md)

4. Push to the branch (`git push origin feature/your-feature`)

5. Create a Pull Request

## License

## Acknowledgments

Distributed under the MIT License. See `LICENSE` for more information.

*   The [PyPSA Community](https://pypsa.org/) and [PyPSA-Meets-Earth Initiative](https://github.com/pypsa-meets-earth/pypsa-earth) for building an incredible open-source ecosystem.

*   [LangChain](https://www.langchain.com/) for providing the powerful framework that makes this possible.## Contributing

*   [discord.py](https://github.com/Rapptz/discord.py) for the robust Discord API wrapper.Contributions are welcome! If you have ideas for new features, improvements to the knowledge ingestion, or bug fixes, please feel free to open an issue or submit a pull request.

*   [Google Gemini](https://ai.google.dev/) for the powerful language models.- Fork the repository.

*   [FAISS](https://faiss.ai/) for the efficient similarity search library.- Create a new branch (git checkout -b feature/your-feature-name).

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