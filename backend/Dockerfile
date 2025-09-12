# Multi-stage Dockerfile for FastAPI backend (Python 3.11)

ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION} AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install uv (fast Python package manager) and then deps for caching
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

# --- Dev target: auto-reload
FROM base AS dev
COPY . .
EXPOSE 8000
CMD ["uvx","uvicorn","main:app","--host","0.0.0.0","--port","8000","--reload"]

# --- Prod target: optimized runtime
FROM base AS prod
COPY . .
EXPOSE 8000
CMD ["uvx","uvicorn","main:app","--host","0.0.0.0","--port","8000"]
