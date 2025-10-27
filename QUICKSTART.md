````markdown
# 🚀 Quick Start Guide

## What This Bot Does

Your PyPSA Helper Bot uses RAG (Retrieval-Augmented Generation) to answer questions about PyPSA by searching through:
- PyPSA core documentation and code
- PyPSA-EUR and PyPSA-Earth repositories
- GitHub issues and discussions

## 📁 Project Structure

- **`src/ingest.py`** - Builds FAISS index from PyPSA repositories
- **`src/bot.py`** - Discord bot that answers questions using the index
- **`.github/workflows/ci.yml`** - Automated testing on every push/PR
- **`.github/workflows/build-index.yml`** - Builds and stores FAISS index as GitHub Release
- **`Dockerfile`** - Container configuration for deployment

## 🎯 Quick Setup (Local Development)

### 1. Clone and Install (5 minutes)

```bash
# Clone the repo
git clone <your-repo-url>
cd pypsa-helper-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables (5 minutes)

```bash
# Copy template
cp .env.example .env

# Edit .env and add your tokens:
# - DISCORD_BOT_TOKEN (from https://discord.com/developers/applications)
# - GOOGLE_API_KEY (from https://makersuite.google.com/app/apikey)
# - GITHUB_ACCESS_TOKEN (from https://github.com/settings/tokens)
```

### 3. Build FAISS Index (1-3 hours, one-time)

```bash
# This downloads PyPSA repos and builds the vector index
python src/ingest.py
```

This creates `pypsa_ecosystem_faiss_index/` directory with the searchable index.

### 4. Run the Bot (1 minute)

```bash
python src/bot.py
```

The bot will connect to Discord and start responding to mentions!

## 🔄 Using GitHub Actions to Build Index

Instead of building the index locally, you can use GitHub Actions:

### 1. Configure GitHub Secrets

Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Where to get it |
|------------|-----------------|
| `GOOGLE_API_KEY` | Google AI Studio (https://makersuite.google.com/app/apikey) |
| `GITHUB_ACCESS_TOKEN` | GitHub Settings → Tokens (needs 'repo' and 'read:org' scopes) |

### 2. Trigger the Workflow

1. Go to GitHub Actions tab
2. Select "Build and Upload FAISS Index"
3. Click "Run workflow"
4. Wait 1-3 hours for it to complete

### 3. Download the Built Index

Once the workflow completes:

1. Go to your repo's Releases page
2. Find the latest release (tagged like `index-20240115-143022`)
3. Download `pypsa-faiss-index.tar.gz`
4. Extract it:

```bash
tar -xzf pypsa-faiss-index.tar.gz
mv pypsa_ecosystem_faiss_index/ .
```

Now you can run the bot locally with the pre-built index!

## 🐳 Running with Docker

### Build the Image

```bash
docker build -t pypsa-bot .
```

### Run the Container

```bash
docker run -d \
  --name pypsa-bot \
  -e DISCORD_BOT_TOKEN="your_token" \
  -e GOOGLE_API_KEY="your_key" \
  -v $(pwd)/pypsa_ecosystem_faiss_index:/app/pypsa_ecosystem_faiss_index:ro \
  pypsa-bot
```

**Note**: You need to have the FAISS index directory available locally and mount it into the container.

## 💡 How It Works

```
User asks question in Discord
   ↓
Bot receives mention
   ↓
Extract question text
   ↓
Search FAISS index for relevant context
   ↓
Send context + question to Google Gemini
   ↓
Return AI-generated answer with citations
```

## 🔧 Development Tips

### Rebuild Index After Updates

```bash
# If PyPSA repos have new content
python src/ingest.py
```

### Test Locally

```bash
# Run with debug output
python src/bot.py
```

### Linting

```bash
# Check code quality
ruff check src/
```

## 📚 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | Yes | Discord bot authentication token |
| `GOOGLE_API_KEY` | Yes | Google Gemini API key for AI responses |
| `GITHUB_ACCESS_TOKEN` | For index building | GitHub token to access repositories |

## 🆘 Troubleshooting

**Bot not responding?**
- Check bot has correct Discord permissions
- Verify bot token is valid
- Check console for error messages

**Index building fails?**
- Verify GitHub token has correct scopes
- Check internet connection
- Ensure enough disk space (~2GB)

**Docker container won't start?**
- Check environment variables are set
- Verify FAISS index directory is mounted
- Review logs: `docker logs pypsa-bot`

## 🎉 Success Checklist

- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] FAISS index built (locally or via GitHub Actions)
- [ ] Bot connects to Discord successfully
- [ ] Bot responds to test questions

## 📞 Next Steps

- **For cloud deployment**: You can deploy the Docker container to any platform (AWS, Azure, GCP, DigitalOcean, etc.)
- **For automation**: The GitHub Actions workflow can run on a schedule to rebuild the index periodically
- **For monitoring**: Add logging and error tracking as needed

---

**Questions?** Check the code comments in `src/bot.py` and `src/ingest.py` for more details! 🚀

````
