# Roadmap — TimeStream Two‑Pass

## Phase 0 — MVP Integration (this PR)
- Two‑pass generator: cognition scratchpad → scorer → public renderer
- WS params: `reflectiveness`, `creativity`, `debug_meta`
- UI controls panel + optional meta viewer
- Minimal tests for cognition shape & scoring

## Phase 1 — Authenticity & Evaluation
- Temporal lexicon gate per era; anachronism audit log
- Style verifier: n‑gram era classifier (baseline)
- Diffusion telemetry: spike half‑lives around event windows
- A/B era affordances (hashtags/RT/quote/thread toggles)

## Phase 2 — Personas with Memory
- Longitudinal belief drift & confidence calibration
- Audience modeling per community (homophily/authority)
- Persuasion micro‑effects from replies/retweets

## Phase 3 — Model Plug‑in Layer
- Swap renderer with local LLM (Ollama or Docker Model Runner)
- Constrained decoding with lexicon & style masks
- Safety filters + defamation/harassment blocks

## How to file work
- **Epics**: cross‑cutting initiatives (use the “Epic” template) — add scope, deps, deliverables.  
- **Features**: “Feature” template with acceptance criteria & priority.  
- **Feature requests**: “Feature request” template for proposals.  
- **Docs**: “Documentation” template for READMEs and guides.  
- **Bugs**: “Bug report” template with repro steps and env details.

> Labels and labeler config are included for `enhancement`, `epic`, `P0–P3`, `frontend`, `services`, etc. Use your org project board link in the templates to track status.
