# TimeStream — Two‑Pass Cognition MVP

A temporally grounded micro‑blog simulator with **two‑pass generation**: a private cognition/meta pass (scratchpad) and a public utterance pass (tweet), plus basic scoring and diffusion.

## Quickstart

### Backend
```bash
cd backend
# Install uv if needed (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install deps with uv
uv venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Run the API (using uvx to launch uvicorn)
uvx uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
bun install
bun run dev -- --host
```
Open the local URL printed by Vite (e.g., http://localhost:5173).

## Two‑Pass Overview
1) **Cognition (private)**: builds a scratchpad with intent, confidence, self‑reference, audience model, and risk assessment.  
2) **Scoring**: temporal plausibility, self‑consistency with persona beliefs, lexicon/voice match.  
3) **Public rendering**: compresses scratchpad into an era‑authentic tweet (char‑limited, optional event tag + citations).

Controls are in the UI (top bar): **Reflectiveness**, **Creativity**, and **Show meta** (debug).

## Docker (optional)
Dev Compose spins up both API (Python) and UI (Bun/Vite):
```bash
docker compose up --build
```
It exposes UI on http://localhost:5173 and API on http://localhost:8000.

compose.yaml overview:
```yaml
services:
  api:
    build:
      context: ./backend
      target: dev   # Uses uv for deps; uvx for uvicorn
    volumes: ["./backend:/app"]
    ports: ["8000:8000"]

  ui:
    build:
      context: ./frontend
      target: dev   # uses Bun to run Vite dev server
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
      - ./frontend/index.html:/app/index.html
      - ./frontend/vite.config.js:/app/vite.config.js
    ports: ["5173:5173"]
    depends_on: [api]
```

Production image for the UI is available via the same Dockerfile:
```bash
docker build -t corvid-ui:prod --target prod frontend
docker run --rm -p 5173:5173 corvid-ui:prod
```

Backend API production image:
```bash
docker build -t corvid-api:prod --target prod backend
docker run --rm -p 8000:8000 corvid-api:prod
```
> For a model-in-container (e.g., Ollama) or Docker Model Runner wiring, add a `MODEL_BASE_URL` to backend and swap the simple renderer with a callout.

## GitHub Workflow
This repo includes your issue templates and label config under `.github/` so you can file **Epics**, **Features**, **Docs**, and **Bugs** using your existing forms. Release automation is pre‑wired via `release-please.config.json`.
