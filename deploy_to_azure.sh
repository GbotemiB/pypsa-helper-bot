#!/bin/bash
set -e

echo "🚀 Deploy to Azure Container Instances"
echo "======================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker username was saved
if [ -f /tmp/docker_username.txt ]; then
    DOCKER_USERNAME=$(cat /tmp/docker_username.txt)
    echo "Found Docker username: $DOCKER_USERNAME"
    read -p "Is this correct? (y/n): " correct
    if [[ $correct != "y" ]]; then
        read -p "Enter your Docker Hub username: " DOCKER_USERNAME
    fi
else
    read -p "Enter your Docker Hub username: " DOCKER_USERNAME
fi

if [[ -z "$DOCKER_USERNAME" ]]; then
    echo -e "${RED}❌ Username cannot be empty${NC}"
    exit 1
fi

echo ""
echo "Your Docker image: $DOCKER_USERNAME/pypsa-helper-bot:latest"
echo ""

read -p "Enter your Discord Bot Token: " DISCORD_BOT_TOKEN
echo ""
read -p "Enter your Google API Key: " GOOGLE_API_KEY

if [[ -z "$DISCORD_BOT_TOKEN" ]] || [[ -z "$GOOGLE_API_KEY" ]]; then
    echo -e "${RED}❌ Both tokens are required${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Select region (Azure for Students restrictions apply):${NC}"
echo "1. Central US (recommended)"
echo "2. West Europe"
echo "3. Southeast Asia"
echo "4. East Asia"
echo ""
read -p "Enter choice (1-4): " region_choice

case $region_choice in
    1) LOCATION="centralus" ;;
    2) LOCATION="westeurope" ;;
    3) LOCATION="southeastasia" ;;
    4) LOCATION="eastasia" ;;
    *) LOCATION="centralus" ;;
esac

echo ""
echo -e "${YELLOW}Deploying to $LOCATION...${NC}"

# Try to create container
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
  --location $LOCATION

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Your bot is deployed!${NC}"
    echo ""
    echo "📊 Useful commands:"
    echo ""
    echo "Check status:"
    echo "  /opt/homebrew/bin/az container show --resource-group pypsa-bot-rg --name pypsa-helper-bot --query instanceView.state"
    echo ""
    echo "View logs:"
    echo "  /opt/homebrew/bin/az container logs --resource-group pypsa-bot-rg --name pypsa-helper-bot --follow"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Deployment failed${NC}"
    echo ""
    echo "This region ($LOCATION) might not be available for Azure for Students."
    echo "Run this script again and try a different region."
    echo ""
    echo "Or check available regions:"
    echo "  /opt/homebrew/bin/az account list-locations --output table"
fi
