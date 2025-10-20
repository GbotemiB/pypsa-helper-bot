# Quick Manual Deployment Guide

Since the automated script is having Docker daemon issues, here's a simple manual process.

## Step 1: Ensure Docker Desktop is Running

1. Open Docker Desktop from Applications
2. Wait until you see the Docker icon in your menu bar showing "Docker Desktop is running"
3. This may take 1-2 minutes

## Step 2: Test Docker

Open a new terminal and run:

```bash
docker --version
```

If it shows a version, Docker is ready!

## Step 3: Build the Image

```bash
cd /Users/gbotemi/Documents/code/pypsa-helper-bot

docker build -t oluwagbotty/pypsa-helper-bot:latest .
```

This will take 5-10 minutes. You'll see lots of output.

## Step 4: Push to Docker Hub

```bash
docker push oluwagbotty/pypsa-helper-bot:latest
```

This uploads the image to Docker Hub (may take a few minutes).

## Step 5: Deploy to Azure

```bash
# Set your tokens (replace with actual values)
DISCORD_BOT_TOKEN="your_discord_bot_token_here"
GOOGLE_API_KEY="your_google_api_key_here"

# Deploy
/opt/homebrew/bin/az container create \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --image oluwagbotty/pypsa-helper-bot:latest \
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

**If centralus doesn't work,** try: `westeurope`, `southeastasia`, or `eastasia`

## Step 6: Check if it's Running

```bash
/opt/homebrew/bin/az container show \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --query instanceView.state
```

Should show: `"Running"`

## Step 7: View Logs

```bash
/opt/homebrew/bin/az container logs \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --follow
```

You should see the bot logging in to Discord!

---

## Common Issues

### "docker: command not found"

**Solution:**  
Add Docker to your PATH:

```bash
echo 'export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Or use the full path: `/Applications/Docker.app/Contents/Resources/bin/docker`

### "Cannot connect to Docker daemon"

**Solution:**  
1. Quit Docker Desktop completely
2. Reopen Docker Desktop
3. Wait 2 minutes
4. Try again

### Docker Desktop not opening

**Solution:**  
```bash
# Check if it's already running
ps aux | grep Docker | grep -v grep

# If yes, try docker commands
# If no, double-click Docker in Applications folder
```

---

## Quick Commands Reference

```bash
# Build image
docker build -t oluwagbotty/pypsa-helper-bot:latest .

# Push to Docker Hub
docker push oluwagbotty/pypsa-helper-bot:latest

# Check Azure container status
/opt/homebrew/bin/az container show --resource-group pypsa-bot-rg --name pypsa-helper-bot --query instanceView.state

# View logs
/opt/homebrew/bin/az container logs --resource-group pypsa-bot-rg --name pypsa-helper-bot --follow

# Restart container
/opt/homebrew/bin/az container restart --resource-group pypsa-bot-rg --name pypsa-helper-bot
```

---

**Start with Step 1!** Make sure Docker Desktop is fully running before proceeding. 🚀
