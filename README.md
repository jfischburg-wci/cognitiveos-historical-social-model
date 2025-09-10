# TimeStream — Two‑Pass Cognition MVP

A temporally grounded micro‑blog simulator with **two‑pass generation**: a private cognition/meta pass (scratchpad) and a public utterance pass (tweet), plus basic scoring and diffusion.

## Quickstart

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host
```
Open the local URL printed by Vite (e.g., http://localhost:5173).

## Two‑Pass Overview
1) **Cognition (private)**: builds a scratchpad with intent, confidence, self‑reference, audience model, and risk assessment.  
2) **Scoring**: temporal plausibility, self‑consistency with persona beliefs, lexicon/voice match.  
3) **Public rendering**: compresses scratchpad into an era‑authentic tweet (char‑limited, optional event tag + citations).

Controls are in the UI (top bar): **Reflectiveness**, **Creativity**, and **Show meta** (debug).

## Docker (optional)
```yaml
# compose.yaml — dev convenience
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ui:
    build: ./frontend
    ports: ["5173:5173"]
    command: ["npm","run","dev","--","--host"]
```
> For a model-in-container (e.g., Ollama) or Docker Model Runner wiring, add a `MODEL_BASE_URL` to backend and swap the simple renderer with a callout.

## GitHub Workflow
This repo includes your issue templates and label config under `.github/` so you can file **Epics**, **Features**, **Docs**, and **Bugs** using your existing forms. Release automation is pre‑wired via `release-please.config.json`.
