# Docker Hub Setup for Azure Deployment

This guide walks you through setting up Docker Hub and configuring GitHub secrets for the Azure deployment workflow.

## Why Docker Hub?

- **FREE** for public repositories (vs $5/month for Azure Container Registry)
- Simple setup - just username and token
- Saves ~$60/year on deployment costs
- Final Azure cost: **~$70/month** (only Azure Container Instances)

## Step 1: Create Docker Hub Account

1. Go to [hub.docker.com](https://hub.docker.com)
2. Sign up for a free account (or log in if you already have one)
3. Verify your email address

## Step 2: Create Access Token

1. Log into Docker Hub
2. Click on your username (top right) → **Account Settings**
3. Go to **Security** tab
4. Click **New Access Token**
5. Fill in:
   - **Description**: "GitHub Actions - PyPSA Helper Bot"
   - **Access permissions**: Select **Read, Write, Delete**
6. Click **Generate**
7. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

## Step 3: Add GitHub Secrets

Go to your GitHub repository: `https://github.com/gbotemi/pypsa-helper-bot/settings/secrets/actions`

Add these 2 new secrets:

### 1. `DOCKERHUB_USERNAME`
- **Value**: Your Docker Hub username (e.g., `gbotemi`)

### 2. `DOCKERHUB_TOKEN`
- **Value**: The access token you just created from Docker Hub

## Step 4: Verify Existing Secrets

Make sure you still have these secrets from the Azure setup:

- ✅ `AZURE_CREDENTIALS` - JSON with service principal credentials
- ✅ `DISCORD_BOT_TOKEN` - Your Discord bot token
- ✅ `GEMINI_API_KEY` - Google Gemini API key

## Step 5: Test Deployment

Once secrets are added:

1. Go to **Actions** tab in GitHub
2. Select **"Deploy to Azure Container Instances"** workflow
3. Click **"Run workflow"** → **"Run workflow"** button
4. Watch the workflow run:
   - ✅ Should login to Docker Hub successfully
   - ✅ Should build and push image to Docker Hub
   - ✅ Should deploy to Azure Container Instances

## Troubleshooting

### "unauthorized: authentication required" error
- Double-check `DOCKERHUB_USERNAME` matches your Docker Hub username exactly
- Verify `DOCKERHUB_TOKEN` was copied completely (no spaces/newlines)
- Check token hasn't expired on Docker Hub

### "repository does not exist" error
- First run will create the repository automatically
- Make sure image name in workflow matches: `docker.io/<your-username>/pypsa-helper-bot`

### Image pull fails in Azure
- Verify image is **public** on Docker Hub (check repository settings on hub.docker.com)
- Check image exists: `docker pull <your-username>/pypsa-helper-bot:latest`

## What Changed?

| Before (ACR) | After (Docker Hub) |
|--------------|-------------------|
| `$AZURE_REGISTRY_NAME.azurecr.io` | `docker.io/$DOCKERHUB_USERNAME` |
| Azure Container Registry setup required | Just Docker Hub account needed |
| 3 GitHub secrets (AZURE_REGISTRY_*) | 2 GitHub secrets (DOCKERHUB_*) |
| ~$75/month total cost | ~$70/month total cost |

## Docker Hub Repository

After first deployment, your images will be at:
- `https://hub.docker.com/r/<your-username>/pypsa-helper-bot`

Each deployment creates a new image tag with the commit SHA.

## Next Steps

After setup is complete:

1. ✅ Add Docker Hub secrets to GitHub
2. ✅ Run deployment workflow
3. ✅ Verify bot starts successfully
4. ✅ Test bot in Discord

See `AZURE_DEPLOYMENT.md` for full deployment documentation.
