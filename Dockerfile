FROM python:3.11-slim AS builder

WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY pypsa_bot/ ./pypsa_bot/

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD ["pypsa-bot", "run"]
