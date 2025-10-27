#!/bin/bash
set -e

echo "🔍 Checking for FAISS index..."

INDEX_DIR="/app/pypsa_ecosystem_faiss_index"
REPO_OWNER="${GITHUB_REPO_OWNER:-GbotemiB}"
REPO_NAME="${GITHUB_REPO_NAME:-pypsa-helper-bot}"

# Check if index already exists
if [ -d "$INDEX_DIR" ] && [ -f "$INDEX_DIR/index.faiss" ] && [ -f "$INDEX_DIR/index.pkl" ]; then
    echo "✅ FAISS index already exists locally"
    exit 0
fi

echo "📥 Downloading latest FAISS index from GitHub Releases..."

# Get the latest release with index tag
API_URL="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases"
echo "Fetching releases from: $API_URL"

RELEASE_DATA=$(curl -s "$API_URL")
DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep -o "https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/index-[^/]*/pypsa-faiss-index.tar.gz" | head -n 1)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "❌ Error: Could not find FAISS index release"
    echo "Please ensure you've run the 'Build FAISS Index' workflow first"
    exit 1
fi

echo "Found index at: $DOWNLOAD_URL"
echo "Downloading..."

# Download the index
curl -L -o /tmp/pypsa-faiss-index.tar.gz "$DOWNLOAD_URL"

echo "Extracting index..."
tar -xzf /tmp/pypsa-faiss-index.tar.gz -C /app/

# Verify extraction
if [ -f "$INDEX_DIR/index.faiss" ] && [ -f "$INDEX_DIR/index.pkl" ]; then
    echo "✅ FAISS index downloaded and extracted successfully"
    rm /tmp/pypsa-faiss-index.tar.gz
    ls -lh "$INDEX_DIR"
else
    echo "❌ Error: Index files not found after extraction"
    exit 1
fi
