# Azure for Students - Simplified Deployment Guide

## 🎓 Student Subscription Limitations

Your Azure for Students subscription has some regional restrictions. Let's use a **simpler deployment method** that works better with student accounts.

## 🚀 Simplified Deployment (No Container Registry Needed!)

Instead of using Azure Container Registry + Container Instances, we'll use **Docker Hub** (free) + **Azure Container Instances**.

### Step 1: Create Docker Hub Account (Free)

1. Go to: https://hub.docker.com/signup
2. Create free account
3. Note your username

### Step 2: Build and Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Build the image
cd /Users/gbotemi/Documents/code/pypsa-helper-bot
docker build -t YOUR_DOCKERHUB_USERNAME/pypsa-helper-bot:latest .

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/pypsa-helper-bot:latest
```

### Step 3: Deploy to Azure Container Instances

```bash
# Set your Docker Hub username
DOCKER_USERNAME="your_dockerhub_username"

# Create container instance
/opt/homebrew/bin/az container create \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --image $DOCKER_USERNAME/pypsa-helper-bot:latest \
  --environment-variables \
    DISCORD_BOT_TOKEN="YOUR_DISCORD_TOKEN" \
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY" \
    INDEX_CHECK_INTERVAL=300 \
    PYTHONUNBUFFERED=1 \
  --cpu 1 \
  --memory 0.5 \
  --restart-policy Always \
  --location westeurope
```

---

## 🔄 Alternative: Use Railway.app Instead

Given the Azure for Students restrictions, **Railway.app might be easier**:

### Why Railway.app?

✅ **$5 free credit per month** (enough for this bot)  
✅ **No credit card required**  
✅ **No regional restrictions**  
✅ **Simpler deployment**  
✅ **GitHub integration** (auto-deploy on push)  

### Quick Railway Setup

1. **Sign up:** https://railway.app (use GitHub account)

2. **Create new project** from GitHub repo

3. **Set environment variables:**
   - `DISCORD_BOT_TOKEN`
   - `GOOGLE_API_KEY`
   - `INDEX_CHECK_INTERVAL=300`
   - `PYTHONUNBUFFERED=1`

4. **Deploy!** Railway auto-detects Dockerfile

5. **Done!** Bot runs 24/7 for free (within $5/month)

---

## 💡 Recommendation

Given your situation:

### Option 1: Try Docker Hub + Azure Container Instances
- Uses your student credits
- Slightly more complex
- Good learning experience

### Option 2: Switch to Railway.app (Recommended!)
- Simpler setup (5 minutes)
- No Azure complications
- Still completely free
- Better for student projects

---

## 📊 Cost Comparison

| Platform | Free Credit | Restrictions | Complexity |
|----------|-------------|--------------|------------|
| **Azure Students** | $100 | Regional limits | High |
| **Railway.app** | $5/month | None | Low |

For a Discord bot, **Railway is simpler and sufficient**.

---

## ❓ What would you prefer?

1. **Continue with Azure** (Docker Hub method)
2. **Switch to Railway.app** (recommended - easier!)

Let me know and I'll help you set it up! 🚀
