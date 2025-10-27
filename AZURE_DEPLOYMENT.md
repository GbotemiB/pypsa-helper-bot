# Azure Deployment Guide

This guide walks you through deploying the PyPSA Discord bot to Azure Container Instances (ACI).

## Prerequisites

1. **Azure Account** with an active subscription
2. **Azure CLI** installed locally (optional, for manual setup)
3. **GitHub Secrets** configured in your repository
4. **FAISS Index** built and released (via `Build FAISS Index` workflow)

## Architecture

The deployment uses:
- **Azure Container Registry (ACR)**: Stores Docker images
- **Azure Container Instances (ACI)**: Runs the Discord bot container
- **GitHub Actions**: Automates build and deployment
- **GitHub Releases**: Stores the FAISS index (downloaded on container startup)

## Setup Steps

### 1. Create Azure Resources

You need to create these Azure resources (one-time setup):

#### Option A: Using Azure Portal (Recommended for beginners)

1. **Create Resource Group:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "Resource groups" → "Create"
   - Name: `pypsa-bot-rg`
   - Region: `East US` (or your preferred region)

2. **Create Container Registry:**
   - Search for "Container registries" → "Create"
   - Name: `pypsabotregistry` (must be globally unique, adjust if needed)
   - Resource group: `pypsa-bot-rg`
   - Location: `East US`
   - SKU: `Basic` (cheapest option, $5/month)
   - Click "Review + Create"

3. **Enable Admin User on Registry:**
   - Go to your Container Registry
   - Settings → Access keys
   - Enable "Admin user"
   - Copy the username and password (you'll need these for GitHub secrets)

4. **Create Service Principal:**
   - Open Azure Cloud Shell (top-right icon in portal)
   - Run:
   ```bash
   az ad sp create-for-rbac \
     --name "pypsa-bot-sp" \
     --role contributor \
     --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/pypsa-bot-rg \
     --sdk-auth
   ```
   - Copy the entire JSON output (you'll need it for GitHub secrets)

#### Option B: Using Azure CLI (Advanced)

```bash
# Login to Azure
az login

# Create resource group
az group create --name pypsa-bot-rg --location eastus

# Create container registry
az acr create \
  --resource-group pypsa-bot-rg \
  --name pypsabotregistry \
  --sku Basic

# Enable admin user
az acr update --name pypsabotregistry --admin-enabled true

# Get registry credentials
az acr credential show --name pypsabotregistry

# Create service principal
az ad sp create-for-rbac \
  --name "pypsa-bot-sp" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/pypsa-bot-rg \
  --sdk-auth
```

### 2. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions → New repository secret):

| Secret Name | Description | Where to Find |
|-------------|-------------|---------------|
| `AZURE_CREDENTIALS` | Service principal JSON | Output from `az ad sp create-for-rbac` command |
| `AZURE_REGISTRY_NAME` | Container registry name | e.g., `pypsabotregistry` |
| `AZURE_REGISTRY_USERNAME` | Registry admin username | Azure Portal → Container Registry → Access keys |
| `AZURE_REGISTRY_PASSWORD` | Registry admin password | Azure Portal → Container Registry → Access keys |
| `DISCORD_BOT_TOKEN` | Your Discord bot token | Already configured |
| `GOOGLE_API_KEY` | Google Gemini API key | Already configured |

**Example AZURE_CREDENTIALS format:**
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### 3. Deploy to Azure

Once everything is set up:

1. **Ensure FAISS Index is Built:**
   - Go to Actions → "Build FAISS Index" → Run workflow
   - Wait for completion (creates a GitHub Release)

2. **Deploy the Bot:**
   - Go to Actions → "Deploy to Azure Container Instances"
   - Click "Run workflow"
   - Select environment (production/staging)
   - Click "Run workflow"

3. **Monitor Deployment:**
   - Watch the workflow progress
   - Check for any errors
   - Deployment takes ~5-10 minutes

### 4. Verify Deployment

#### Check Container Status in Azure Portal:
1. Go to Resource groups → `pypsa-bot-rg`
2. Click on `pypsa-discord-bot` container instance
3. Check "Containers" tab → "Events" for logs
4. Verify status is "Running"

#### View Container Logs:
```bash
az container logs \
  --resource-group pypsa-bot-rg \
  --name pypsa-discord-bot
```

You should see:
```
🔍 Checking for FAISS index...
📥 Downloading latest FAISS index from GitHub Releases...
✅ FAISS index downloaded and extracted successfully
Vector store loaded successfully.
Bot logged in as PyPSA-AI-Helper#1234
```

#### Test the Bot:
1. Go to your Discord server
2. Type a message mentioning the bot
3. Ask a PyPSA-related question

## Configuration

### Resource Specifications

Current configuration (in `deploy-azure.yml`):
- **CPU**: 2 cores
- **Memory**: 4 GB
- **Restart Policy**: Always (auto-restarts on failure)

To modify:
```yaml
cpu: 2        # Increase for better performance
memory: 4     # Increase if bot runs out of memory
```

### Environment Variables

Set in the workflow file:
```yaml
environment-variables: |
  DISCORD_BOT_TOKEN=${{ secrets.DISCORD_BOT_TOKEN }}
  GOOGLE_API_KEY=${{ secrets.GOOGLE_API_KEY }}
  GITHUB_REPO_OWNER=GbotemiB
  GITHUB_REPO_NAME=pypsa-helper-bot
```

## Cost Estimate

Azure Container Instances pricing (as of 2025):
- **Container Registry (Basic)**: ~$5/month
- **ACI (2 vCPU, 4 GB RAM)**: ~$70/month (running 24/7)

**Total**: ~$75/month

### Cost Optimization Tips:

1. **Use smaller resources:**
   - Try 1 vCPU, 2 GB RAM first (~$35/month)
   - Monitor performance and scale up if needed

2. **Stop when not needed:**
   ```bash
   az container stop --resource-group pypsa-bot-rg --name pypsa-discord-bot
   az container start --resource-group pypsa-bot-rg --name pypsa-discord-bot
   ```

3. **Delete when testing:**
   ```bash
   az container delete --resource-group pypsa-bot-rg --name pypsa-discord-bot
   ```

## Troubleshooting

### Bot not responding in Discord:

1. **Check container logs:**
   ```bash
   az container logs --resource-group pypsa-bot-rg --name pypsa-discord-bot --follow
   ```

2. **Verify environment variables:**
   - Check secrets are set correctly in GitHub
   - Ensure no trailing spaces or newlines

3. **Check FAISS index download:**
   - Look for "✅ FAISS index downloaded" in logs
   - Verify GitHub Release exists with `pypsa-faiss-index.tar.gz`

### Deployment fails:

1. **Authentication issues:**
   - Verify `AZURE_CREDENTIALS` JSON is valid
   - Check service principal has contributor role

2. **Registry access denied:**
   - Verify registry admin user is enabled
   - Check username/password secrets are correct

3. **Resource already exists:**
   ```bash
   # Delete existing container
   az container delete --resource-group pypsa-bot-rg --name pypsa-discord-bot --yes
   ```

### Out of memory errors:

- Increase memory in workflow:
  ```yaml
  memory: 8  # Increase to 8 GB
  ```

## Updating the Bot

### Code Changes:
1. Push changes to `main` branch
2. Run "Deploy to Azure Container Instances" workflow
3. New container will be created with updated code

### Update FAISS Index:
1. Run "Build FAISS Index" workflow
2. Run "Deploy to Azure Container Instances" workflow
3. Container will download the new index on startup

## Monitoring

### View Logs:
```bash
# Real-time logs
az container logs --resource-group pypsa-bot-rg --name pypsa-discord-bot --follow

# Recent logs
az container logs --resource-group pypsa-bot-rg --name pypsa-discord-bot --tail 100
```

### Check Status:
```bash
az container show \
  --resource-group pypsa-bot-rg \
  --name pypsa-discord-bot \
  --query "{Status:instanceView.state,IP:ipAddress.ip,CPU:containers[0].resources.requests.cpu,Memory:containers[0].resources.requests.memoryInGb}" \
  --output table
```

### Restart Container:
```bash
az container restart --resource-group pypsa-bot-rg --name pypsa-discord-bot
```

## Cleanup

To delete all Azure resources:

```bash
# Delete the entire resource group (removes everything)
az group delete --name pypsa-bot-rg --yes --no-wait
```

## Alternative Deployment Options

### Azure Container Apps (Better for production):
- Auto-scaling
- Built-in load balancing
- Better monitoring
- Slightly more expensive

### Azure Kubernetes Service (AKS):
- Full Kubernetes cluster
- Best for multiple services
- More complex setup
- Higher cost

### Azure App Service:
- Web app deployment
- Easy scaling
- Good for HTTP-based bots
- Not ideal for Discord bots

## Security Best Practices

1. **Use Key Vault for secrets:**
   - Store tokens in Azure Key Vault
   - Reference in container deployment

2. **Enable managed identity:**
   - Avoid storing credentials in container

3. **Restrict network access:**
   - Use virtual networks if needed
   - Configure firewall rules

4. **Regular updates:**
   - Update base Docker image regularly
   - Keep dependencies up to date

## Support

If you encounter issues:
1. Check container logs first
2. Verify GitHub secrets are correct
3. Ensure FAISS index exists in releases
4. Review Azure deployment events

For Azure-specific issues, refer to:
- [Azure Container Instances Documentation](https://docs.microsoft.com/en-us/azure/container-instances/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)
