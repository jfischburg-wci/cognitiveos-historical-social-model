QA Visual Captures

This folder stores visual QA artifacts and the Playwright config/specs used to generate them. Use these captures to verify animation mapping, seams, resets, and live-site fidelity.

Prereqs
- Bun: install and use from `frontend/`
- Playwright browsers: `cd frontend && bunx playwright install chromium`

Local App (Preview) — Full Actions Suite
- Purpose: Validate mapping, neutral pose reset, and seams across actions using the built build + preview server.
- Command:
  - `cd frontend && bun run test:e2e`
- Config/spec:
  - `frontend/tests/playwright.config.ts` (starts Vite preview on :4173)
  - `frontend/tests/specs/actions.spec.ts`
- Output:
  - `docs/qa/actions-seams-reset-artifacts/*-neutral.png`
  - `docs/qa/actions-seams-reset-artifacts/*-mid.png`
  - `docs/qa/actions-seams-reset-artifacts/*-end.png`

Live Site — Blink at 200% and 100% Zoom
- Purpose: Confirm eyelid closure on the production site (GitHub Pages) with realistic zoom factors.
- 200% zoom:
  - `cd frontend && bunx playwright test -c tests/playwright.live.config.ts tests/specs/live-blink.spec.ts`
  - Config: `frontend/tests/playwright.live.config.ts` (deviceScaleFactor: 2)
  - Spec:   `frontend/tests/specs/live-blink.spec.ts`
- 100% zoom:
  - `cd frontend && bunx playwright test -c tests/playwright.live1x.config.ts tests/specs/live-blink-1x.spec.ts`
  - Config: `frontend/tests/playwright.live1x.config.ts` (deviceScaleFactor: 1)
  - Spec:   `frontend/tests/specs/live-blink-1x.spec.ts`
- Output:
  - `docs/qa/live/blink-live-neutral-200.png`
  - `docs/qa/live/blink-live-mid-200.png`
  - `docs/qa/live/blink-live-end-200.png`
  - `docs/qa/live/blink-live-neutral-100.png`
  - `docs/qa/live/blink-live-mid-100.png`
  - `docs/qa/live/blink-live-end-100.png`

Notes & Tips
- GitHub Pages caches for ~10 minutes; hard refresh or wait after deploys.
- Blink timing: mid/end waits are tuned to current easing; adjust in specs if behavior changes.
- The app exposes `window.rig` when ready; specs call `reset()` before captures.
- To update baselines, re-run the commands above and commit the new PNGs.

