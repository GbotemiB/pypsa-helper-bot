#!/bin/bash
# Quick setup script for Fly.io secrets

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      PyPSA Helper Bot - Fly.io Secrets Setup            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if flyctl is available
if ! command -v flyctl &> /dev/null; then
    echo "❌ Error: flyctl command not found"
    echo "Install it with: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

echo "This script will help you set up Fly.io secrets."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Create it with: cp .env.sample .env"
    exit 1
fi

echo "Loading secrets from .env file..."
source .env

echo ""
echo "Setting Fly.io secrets..."
echo ""

# Set DISCORD_BOT_TOKEN
if [ -n "$DISCORD_BOT_TOKEN" ]; then
    echo "→ Setting DISCORD_BOT_TOKEN..."
    flyctl secrets set DISCORD_BOT_TOKEN="$DISCORD_BOT_TOKEN"
else
    echo "⚠️  Warning: DISCORD_BOT_TOKEN not found in .env"
fi

# Set GOOGLE_API_KEY
if [ -n "$GOOGLE_API_KEY" ]; then
    echo "→ Setting GOOGLE_API_KEY..."
    flyctl secrets set GOOGLE_API_KEY="$GOOGLE_API_KEY"
else
    echo "⚠️  Warning: GOOGLE_API_KEY not found in .env"
fi

# Set GitHub repo info
echo "→ Setting GITHUB_REPO_OWNER..."
flyctl secrets set GITHUB_REPO_OWNER="GbotemiB"

echo "→ Setting GITHUB_REPO_NAME..."
flyctl secrets set GITHUB_REPO_NAME="pypsa-helper-bot"

# Set GITHUB_TOKEN if available
if [ -n "$GITHUB_ACCESS_TOKEN" ]; then
    echo "→ Setting GITHUB_TOKEN..."
    flyctl secrets set GITHUB_TOKEN="$GITHUB_ACCESS_TOKEN"
elif [ -n "$GITHUB_TOKEN" ]; then
    echo "→ Setting GITHUB_TOKEN..."
    flyctl secrets set GITHUB_TOKEN="$GITHUB_TOKEN"
else
    echo "⚠️  Info: GITHUB_TOKEN not found in .env (optional)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Secrets setup complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "Verifying secrets..."
flyctl secrets list

echo ""
echo "Next steps:"
echo "  1. Set GitHub secrets (see NEXT_STEPS.md)"
echo "  2. Run reindex workflow or generate index locally"
echo "  3. Deploy: flyctl deploy"
echo ""
echo "For detailed instructions, see: NEXT_STEPS.md"
