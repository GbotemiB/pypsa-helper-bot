# Deployment Guide — Oracle Cloud Always Free

## Overview

The bot runs on Oracle Cloud's Always Free ARM VM (4 vCPU, 24GB RAM).
This is a truly free tier — no trial, no credit card surprises.

## 1. Provision the VM

1. Log in to Oracle Cloud: https://cloud.oracle.com
2. Create a Compute Instance:
   - Shape: VM.Standard.A1.Flex (ARM)
   - OCPUs: 4, Memory: 24GB
   - Image: Ubuntu 22.04
   - SSH key: upload your public key
3. Open port 6333 in the Security List (for Qdrant, internal only)

## 2. Install Docker

```bash
ssh ubuntu@<your-vm-ip>
sudo apt-get update && sudo apt-get install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in
```

## 3. Deploy the Bot

```bash
git clone https://github.com/GbotemiB/pypsa-helper-bot.git
cd pypsa-helper-bot
git checkout revamp/v2

# Set up environment
cp .env.sample .env
nano .env  # Fill in DISCORD_TOKEN, GROQ_API_KEY, GITHUB_TOKEN

# Start everything
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:6333/health

# Run initial ingestion
docker-compose exec bot pypsa-bot ingest
```

## 4. Auto-restart on Reboot

Docker Compose with `restart: always` handles this.
Verify: `sudo systemctl enable docker`

## 5. Monitoring

```bash
# View bot logs
docker-compose logs -f bot

# View Qdrant logs
docker-compose logs -f qdrant

# Check Qdrant collection info
curl http://localhost:6333/collections/pypsa_docs
```

## 6. Updating

```bash
cd pypsa-helper-bot
git pull
docker-compose build bot
docker-compose up -d bot
```
