# Docker Hub + Azure Deployment Guide

This guide will help you deploy the PyPSA Helper Bot using **Docker Hub** (free) + **Azure Container Instances** (works with Azure for Students).

## 📋 Prerequisites

Before starting, make sure you have:

- ✅ Azure CLI installed (`/opt/homebrew/bin/az --version`)
- ✅ Azure for Students subscription active
- ✅ Logged in to Azure (`/opt/homebrew/bin/az login`)
- ✅ Resource group created (`pypsa-bot-rg`)
- ✅ Docker Desktop installed (at `/Applications/Docker.app`)

## 🚀 Quick Start (Easy Way)

### Option 1: Automated Script

Run the all-in-one script:

```bash
./setup_docker_deploy.sh
```

This will:
1. ✅ Start Docker Desktop if needed
2. ✅ Prompt for Docker Hub credentials
3. ✅ Build the Docker image
4. ✅ Push to Docker Hub
5. ✅ Deploy to Azure Container Instances
6. ✅ Set up all environment variables

---

## 📖 Manual Step-by-Step (If You Prefer)

### Step 1: Create Docker Hub Account

1. Go to: https://hub.docker.com/signup
2. Create a free account
3. Note your username

### Step 2: Start Docker Desktop

```bash
open -a Docker
```

Wait for Docker to fully start (30-60 seconds).

### Step 3: Login to Docker Hub

```bash
/Applications/Docker.app/Contents/Resources/bin/docker login
```

Enter your Docker Hub username and password.

### Step 4: Build the Docker Image

```bash
# Replace YOUR_USERNAME with your Docker Hub username
DOCKER_USERNAME="your_dockerhub_username"

/Applications/Docker.app/Contents/Resources/bin/docker build \
  -t $DOCKER_USERNAME/pypsa-helper-bot:latest .
```

This will take 5-10 minutes.

### Step 5: Push to Docker Hub

```bash
/Applications/Docker.app/Contents/Resources/bin/docker push \
  $DOCKER_USERNAME/pypsa-helper-bot:latest
```

This uploads your image to Docker Hub (free, unlimited public images).

### Step 6: Deploy to Azure

```bash
# Set your credentials
DOCKER_USERNAME="your_dockerhub_username"
DISCORD_BOT_TOKEN="your_discord_bot_token"
GOOGLE_API_KEY="your_google_api_key"

# Deploy to Azure Container Instances
/opt/homebrew/bin/az container create \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --image $DOCKER_USERNAME/pypsa-helper-bot:latest \
  --environment-variables \
    DISCORD_BOT_TOKEN="$DISCORD_BOT_TOKEN" \
    GOOGLE_API_KEY="$GOOGLE_API_KEY" \
    INDEX_CHECK_INTERVAL=300 \
    PYTHONUNBUFFERED=1 \
    GITHUB_REPO_OWNER=GbotemiB \
    GITHUB_REPO_NAME=pypsa-helper-bot \
  --cpu 1 \
  --memory 0.5 \
  --restart-policy Always \
  --location centralus
```

**Note:** If `centralus` doesn't work (Azure for Students restrictions), try:
- `westeurope`
- `southeastasia`
- `eastasia`

---

## 🔍 Verify Deployment

### Check Container Status

```bash
/opt/homebrew/bin/az container show \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --query instanceView.state
```

Should show: `"Running"`

### View Logs

```bash
/opt/homebrew/bin/az container logs \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --follow
```

You should see:
```
Logged in as PyPSA Helper Bot#1234
Bot is ready!
```

---

## 🔄 Update Deployment

When you make code changes:

### Method 1: Using Script

```bash
./setup_docker_deploy.sh
```

Just rebuild and push, skip deployment if already running.

### Method 2: Manual

```bash
# 1. Rebuild image
/Applications/Docker.app/Contents/Resources/bin/docker build \
  -t $DOCKER_USERNAME/pypsa-helper-bot:latest .

# 2. Push to Docker Hub
/Applications/Docker.app/Contents/Resources/bin/docker push \
  $DOCKER_USERNAME/pypsa-helper-bot:latest

# 3. Restart container (pulls new image)
/opt/homebrew/bin/az container restart \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot
```

---

## 📊 Management Commands

### View Container Details

```bash
/opt/homebrew/bin/az container show \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot
```

### Restart Container

```bash
/opt/homebrew/bin/az container restart \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot
```

### Stop Container

```bash
/opt/homebrew/bin/az container stop \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot
```

### Delete Container

```bash
/opt/homebrew/bin/az container delete \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --yes
```

### View Real-Time Logs

```bash
/opt/homebrew/bin/az container logs \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --follow
```

---

## 🐛 Troubleshooting

### Docker not found

**Problem:** `zsh: command not found: docker`

**Solution:**
```bash
# Use full path
/Applications/Docker.app/Contents/Resources/bin/docker

# Or add to PATH in ~/.zshrc:
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

### Docker daemon not running

**Problem:** `Cannot connect to the Docker daemon`

**Solution:**
```bash
open -a Docker
# Wait 30-60 seconds for Docker to start
```

### Region not available

**Problem:** `RequestDisallowedByAzure`

**Solution:** Try different regions:
```bash
# List available regions
/opt/homebrew/bin/az account list-locations --output table

# Try: westeurope, southeastasia, eastasia
```

### Container keeps restarting

**Problem:** Container status shows `Waiting` or `Terminated`

**Check logs:**
```bash
/opt/homebrew/bin/az container logs \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot
```

**Common issues:**
- Missing environment variables (DISCORD_BOT_TOKEN, GOOGLE_API_KEY)
- Invalid Discord token
- FAISS index not found (run reindex workflow first)

### Out of student credits

**Problem:** Deployment fails due to quota

**Check usage:**
```bash
# Visit Azure Portal
open https://portal.azure.com

# Check: Cost Management + Billing
```

**Solution:** Consider Railway.app as free alternative

---

## 💰 Cost Estimate

**Azure Container Instances:**
- 1 vCPU + 0.5GB RAM running 24/7
- Cost: ~$67/month
- **Your student credit:** $100
- **Runtime:** ~1.5 months free

**After credits run out:**
- Switch to Railway.app ($5/month free)
- Or self-host (free)

---

## 🎯 Next Steps

1. ✅ Run `./setup_docker_deploy.sh`
2. ✅ Verify bot is running with `/opt/homebrew/bin/az container logs`
3. ✅ Test bot in Discord
4. ✅ Run reindex workflow to generate FAISS index
5. ✅ Monitor usage in Azure Portal

---

## 📚 Additional Resources

- **Docker Hub:** https://hub.docker.com
- **Azure Portal:** https://portal.azure.com
- **Cost Management:** https://portal.azure.com/#view/Microsoft_Azure_CostManagement
- **Azure Students:** https://azure.microsoft.com/free/students/

---

**Ready to deploy?** Run `./setup_docker_deploy.sh` and follow the prompts! 🚀
