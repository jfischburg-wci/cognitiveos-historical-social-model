# Multi-stage Dockerfile for Bun + Vite (Svelte) frontend
ARG BUN_VERSION=1.2.18

FROM oven/bun:${BUN_VERSION} AS base
WORKDIR /app

# Install dependencies first for better caching
COPY --chown=bun:bun package.json bun.lock* ./
RUN bun install

# Bring in the rest of the app
COPY --chown=bun:bun . .

# --- Dev target: runs Vite dev server ---
FROM base AS dev
EXPOSE 5173
CMD ["bun","run","dev","--","--host","0.0.0.0"]

# --- Prod target: build & preview static dist ---
FROM base AS prod
RUN bun run build
EXPOSE 5173
CMD ["bun","run","preview","--","--host","0.0.0.0","--port","5173"]

