#!/bin/bash
set -e

echo "🐳 PyPSA Helper Bot - Docker Hub Deployment Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${YELLOW}Step 1: Checking Docker...${NC}"
if ! /Applications/Docker.app/Contents/Resources/bin/docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Docker is not running. Starting Docker Desktop...${NC}"
    open -a Docker
    echo "⏳ Waiting for Docker to start (this may take 30-60 seconds)..."
    
    # Wait for Docker to be ready
    while ! /Applications/Docker.app/Contents/Resources/bin/docker info > /dev/null 2>&1; do
        sleep 2
        echo -n "."
    done
    echo ""
    echo -e "${GREEN}✅ Docker is running!${NC}"
else
    echo -e "${GREEN}✅ Docker is already running${NC}"
fi

echo ""
echo -e "${YELLOW}Step 2: Docker Hub Setup${NC}"
echo "Before we continue, you need a Docker Hub account."
echo ""
echo "1. Go to: https://hub.docker.com/signup"
echo "2. Create a free account"
echo "3. Come back here"
echo ""
read -p "Do you have a Docker Hub account? (y/n): " has_account

if [[ $has_account != "y" ]]; then
    echo ""
    echo "Please create a Docker Hub account first, then run this script again."
    exit 0
fi

echo ""
read -p "Enter your Docker Hub username: " DOCKER_USERNAME

if [[ -z "$DOCKER_USERNAME" ]]; then
    echo -e "${RED}❌ Username cannot be empty${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Docker Hub Login${NC}"
echo "You'll be prompted for your Docker Hub password..."
/Applications/Docker.app/Contents/Resources/bin/docker login

echo ""
echo -e "${YELLOW}Step 4: Building Docker image...${NC}"
echo "This may take 5-10 minutes..."
/Applications/Docker.app/Contents/Resources/bin/docker build -t $DOCKER_USERNAME/pypsa-helper-bot:latest .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 5: Pushing to Docker Hub...${NC}"
echo "This may take a few minutes depending on your internet speed..."
/Applications/Docker.app/Contents/Resources/bin/docker push $DOCKER_USERNAME/pypsa-helper-bot:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker push failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Image successfully pushed to Docker Hub!${NC}"
echo ""
echo "Your image is available at: https://hub.docker.com/r/$DOCKER_USERNAME/pypsa-helper-bot"
echo ""

# Save username for next step
echo $DOCKER_USERNAME > /tmp/docker_username.txt

echo -e "${YELLOW}Step 6: Deploy to Azure${NC}"
echo "Now we'll deploy the container to Azure Container Instances..."
echo ""
read -p "Do you have your Discord Bot Token ready? (y/n): " has_discord_token

if [[ $has_discord_token != "y" ]]; then
    echo ""
    echo "You need these before deploying:"
    echo "1. Discord Bot Token (from https://discord.com/developers/applications)"
    echo "2. Google API Key (from https://aistudio.google.com/apikey)"
    echo ""
    echo "Get these ready and run: ./deploy_to_azure.sh"
    exit 0
fi

read -p "Enter your Discord Bot Token: " DISCORD_BOT_TOKEN
echo ""
read -p "Enter your Google API Key: " GOOGLE_API_KEY

if [[ -z "$DISCORD_BOT_TOKEN" ]] || [[ -z "$GOOGLE_API_KEY" ]]; then
    echo -e "${RED}❌ Both tokens are required${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Deploying to Azure Container Instances...${NC}"

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

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Azure deployment failed${NC}"
    echo "Try a different region if centralus didn't work."
    echo "Run: ./deploy_to_azure.sh to try again with different settings"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 SUCCESS! Your bot is now deployed!${NC}"
echo ""
echo "📊 Check deployment status:"
echo "   /opt/homebrew/bin/az container show --resource-group pypsa-bot-rg --name pypsa-helper-bot --query instanceView.state"
echo ""
echo "📋 View logs:"
echo "   /opt/homebrew/bin/az container logs --resource-group pypsa-bot-rg --name pypsa-helper-bot --follow"
echo ""
echo "🔄 Restart container:"
echo "   /opt/homebrew/bin/az container restart --resource-group pypsa-bot-rg --name pypsa-helper-bot"
echo ""
echo "🛑 Stop container:"
echo "   /opt/homebrew/bin/az container stop --resource-group pypsa-bot-rg --name pypsa-helper-bot"
echo ""
