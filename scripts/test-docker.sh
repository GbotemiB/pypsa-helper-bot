#!/bin/bash

# Test Docker deployment locally before pushing to Azure

echo "🧪 Testing Docker deployment locally..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env with:"
    echo "  DISCORD_BOT_TOKEN=your_token"
    echo "  GOOGLE_API_KEY=your_key"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t pypsa-helper-bot:test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"
echo ""

# Test the index download script
echo "📥 Testing FAISS index download..."
docker run --rm \
  -e GITHUB_REPO_OWNER=GbotemiB \
  -e GITHUB_REPO_NAME=pypsa-helper-bot \
  pypsa-helper-bot:test \
  sh -c "./scripts/download-index.sh"

if [ $? -ne 0 ]; then
    echo "❌ Index download test failed"
    echo "Make sure you've run the 'Build FAISS Index' workflow first"
    exit 1
fi

echo "✅ Index download test passed"
echo ""

# Optionally run the full container (commented out by default)
echo "To run the full container with Discord bot, uncomment and run:"
echo "docker run --rm --env-file .env pypsa-helper-bot:test"
echo ""
echo "Or test interactively:"
echo "docker run -it --env-file .env pypsa-helper-bot:test /bin/bash"
echo ""
echo "✅ All tests passed! Ready for Azure deployment."
