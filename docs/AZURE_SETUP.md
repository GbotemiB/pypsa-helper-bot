# Azure Container Instances Setup Guide

This guide will help you deploy the PyPSA Helper Bot to Azure Container Instances (ACI) using the Azure Free Tier.

## 📋 Prerequisites

- Azure account (student account or regular account)
- Azure CLI installed
- GitHub account
- Docker installed (for local testing)

## 🎓 Azure for Students

If you have a student email (.edu), you can get:
- **$100 Azure credit** for 12 months
- **Free services** including:
  - 750 hours/month of B1S virtual machines (1 vCPU, 1GB RAM)
  - 5GB blob storage
  - Free tier of Container Registry (50GB storage, unlimited pulls)

**Sign up:** https://azure.microsoft.com/en-us/free/students/

No credit card required for students!

## 🆓 Azure Free Account (Non-students)

If you're not a student:
- **$200 credit** for 30 days
- **12 months of popular free services**
- **Always free services** (limited quantities)

**Note:** This requires a credit card for verification, but you won't be charged unless you upgrade.

---

## 🚀 Step-by-Step Setup

### Step 1: Install Azure CLI

**macOS:**
```bash
curl -L https://aka.ms/InstallAzureCli | bash
```

**Linux:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Windows:**
Download from: https://aka.ms/installazurecliwindows

### Step 2: Login to Azure

```bash
az login
```

This will open your browser for authentication.

### Step 3: Create Resource Group

```bash
# Set your preferred region (choose closest to you)
# Options: eastus, westus, westeurope, eastasia, etc.
LOCATION="eastus"

# Create resource group
az group create \
  --name pypsa-bot-rg \
  --location $LOCATION
```

### Step 4: Create Container Registry

```bash
# Create a container registry (must be globally unique)
REGISTRY_NAME="pypsabotregistry$(date +%s)"

az acr create \
  --resource-group pypsa-bot-rg \
  --name $REGISTRY_NAME \
  --sku Basic \
  --location $LOCATION

# Enable admin access
az acr update \
  --name $REGISTRY_NAME \
  --admin-enabled true

# Get credentials
az acr credential show --name $REGISTRY_NAME
```

**Save these credentials!** You'll need:
- Registry name
- Username
- Password

### Step 5: Build and Push Docker Image

```bash
# Login to Azure Container Registry
az acr login --name $REGISTRY_NAME

# Build and push the image
docker build -t $REGISTRY_NAME.azurecr.io/pypsa-helper-bot:latest .
docker push $REGISTRY_NAME.azurecr.io/pypsa-helper-bot:latest
```

### Step 6: Create Azure Service Principal

This allows GitHub Actions to deploy to Azure:

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac \
  --name "pypsa-bot-deploy" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/pypsa-bot-rg \
  --sdk-auth
```

**Copy the entire JSON output!** You'll need it for GitHub secrets.

### Step 7: Deploy the Container

```bash
# Get registry credentials
REGISTRY_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Deploy container
az container create \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --image $REGISTRY_NAME.azurecr.io/pypsa-helper-bot:latest \
  --registry-login-server $REGISTRY_NAME.azurecr.io \
  --registry-username $REGISTRY_USERNAME \
  --registry-password $REGISTRY_PASSWORD \
  --environment-variables \
    DISCORD_BOT_TOKEN="YOUR_DISCORD_TOKEN" \
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY" \
    INDEX_CHECK_INTERVAL=300 \
    PYTHONUNBUFFERED=1 \
  --cpu 1 \
  --memory 0.5 \
  --restart-policy Always
```

### Step 8: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value | Where to Get It |
|------------|-------|----------------|
| `AZURE_CREDENTIALS` | JSON from Step 6 | Service principal output |
| `AZURE_REGISTRY_NAME` | Your registry name | From Step 4 |
| `AZURE_REGISTRY_USERNAME` | Registry username | `az acr credential show` |
| `AZURE_REGISTRY_PASSWORD` | Registry password | `az acr credential show` |
| `AZURE_RESOURCE_GROUP` | `pypsa-bot-rg` | From Step 3 |
| `DISCORD_BOT_TOKEN` | Your Discord token | Discord Developer Portal |
| `GOOGLE_API_KEY` | Your Google API key | Google AI Studio |

### Step 9: Verify Deployment

```bash
# Check container status
az container show \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --query instanceView.state

# View logs
az container logs \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --follow
```

---

## 📊 Monitoring and Management

### View Container Logs
```bash
az container logs \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --follow
```

### Restart Container
```bash
az container restart \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot
```

### Update Container (after code changes)
```bash
# GitHub Actions will do this automatically, but manually:
az container delete \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --yes

# Then recreate with new image (Step 7)
```

### Check Resource Usage
```bash
az container show \
  --resource-group pypsa-bot-rg \
  --name pypsa-helper-bot \
  --query containers[0].instanceView.currentState
```

---

## 💰 Cost Estimation

**Azure Container Instances Pricing (US East):**
- **Memory:** $0.0000013/GB-second (~$0.0936/GB-hour)
- **CPU:** $0.0000125/vCPU-second (~$0.045/vCPU-hour)

**For this bot (1 vCPU, 0.5GB RAM, 24/7):**
- CPU: 1 × $0.045/hour × 730 hours/month = **~$32.85/month**
- Memory: 0.5GB × $0.0936/GB-hour × 730 hours/month = **~$34.16/month**
- **Total: ~$67/month**

**With Azure for Students ($100 credit):**
- **~1.5 months free**, then you'll need to upgrade or use a different service

**With Azure Free Trial ($200 credit):**
- **~3 months free**

---

## 🔄 Alternatives to Consider

If you want truly free hosting:

### 1. **Railway.app**
- $5 free credit/month (enough for small bots)
- No credit card required
- Simpler than Azure
- https://railway.app

### 2. **Render.com**
- Free tier for background workers
- 750 hours/month free (enough for 24/7)
- Sleeps after 15 min inactivity (not ideal for Discord bots)
- https://render.com

### 3. **Google Cloud Run**
- $300 free credit for 90 days
- Always-free tier (limited)
- Pay only when running
- https://cloud.google.com/run

### 4. **Self-hosting**
- Raspberry Pi at home (one-time cost ~$50)
- Old laptop/desktop
- 100% free ongoing
- You control everything

---

## 🐛 Troubleshooting

### Container keeps restarting
```bash
# Check logs for errors
az container logs --resource-group pypsa-bot-rg --name pypsa-helper-bot
```

Common issues:
- Missing environment variables (DISCORD_BOT_TOKEN, GOOGLE_API_KEY)
- FAISS index not found (run reindex workflow first)
- Invalid Discord token

### "Resource not found" errors
Make sure you're using the correct:
- Resource group name (`pypsa-bot-rg`)
- Container name (`pypsa-helper-bot`)
- Registry name (from Step 4)

### GitHub Actions failing
Check that all secrets are set correctly:
```bash
# Verify your service principal can access the resource group
az group show --name pypsa-bot-rg
```

---

## 🎯 Next Steps

1. ✅ Complete this setup
2. 📦 Generate FAISS index (manually run reindex workflow)
3. 🚀 Deploy via GitHub Actions (automatic on push to main)
4. 🧪 Test the bot in Discord
5. 📊 Monitor logs and resource usage

---

## 📚 Additional Resources

- [Azure Container Instances Documentation](https://docs.microsoft.com/azure/container-instances/)
- [Azure for Students](https://azure.microsoft.com/free/students/)
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)

---

**Questions?** Check the main [README.md](../README.md) or create an issue on GitHub.
