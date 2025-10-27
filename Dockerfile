# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY src/ ./src/
COPY scripts/ ./scripts/

RUN mkdir -p /app/pypsa_ecosystem_faiss_index && \
    chmod +x ./scripts/download-index.sh

ENV PYTHONUNBUFFERED=1

# Download index and start bot
CMD ["sh", "-c", "./scripts/download-index.sh && python src/bot.py"]
