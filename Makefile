# Root Makefile for common tasks across the repo
# Requires: bun, gh (optional for deploy), playwright browsers

# Variables
FRONTEND := frontend
BACKEND  := backend
PROD_URL := https://corvid.contentguru.ai
PAGES_WORKFLOW := pages.yml

.PHONY: help all setup dev build preview test-e2e qa-actions qa-live-200 qa-live-100 qa-live-caw-200 qa-live-caw-100 qa-live-hop-200 qa-live-hop-100 qa-live-walk-200 qa-live-walk-100 typecheck lint format clean ci deploy deploy-force prod-url \
        be-setup be-run be-test be-health \
        be-docker-build-dev be-docker-run-dev be-docker-build-prod be-docker-run-prod compose-up compose-down

help:
	@echo "Available targets:"
	@echo "  setup         - Install frontend deps and Playwright browsers"
	@echo "  all           - Build frontend and trigger deploy"
	@echo "  dev           - Run Vite dev server (frontend)"
	@echo "  build         - Build frontend for production"
	@echo "  preview       - Serve built frontend preview (:4173)"
	@echo "  test-e2e      - Run Playwright e2e suite (local preview)"
	@echo "  qa-actions    - Alias for test-e2e (captures action screenshots)"
	@echo "  qa-live-200   - Capture live blink at 200% zoom"
	@echo "  qa-live-100   - Capture live blink at 100% zoom"
	@echo "  qa-live-caw-200 - Capture live caw at 200% zoom"
	@echo "  qa-live-caw-100 - Capture live caw at 100% zoom"
	@echo "  qa-live-hop-200 - Capture live hop at 200% zoom"
	@echo "  qa-live-hop-100 - Capture live hop at 100% zoom"
	@echo "  qa-live-walk-200 - Capture live walk at 200% zoom"
	@echo "  qa-live-walk-100 - Capture live walk at 100% zoom"
	@echo "  typecheck     - Run svelte-check across Svelte code"
	@echo "  lint          - Prettier check common source files"
	@echo "  format        - Prettier write common source files"
	@echo "  clean         - Remove build/test artifacts"
	@echo "  ci            - Backend tests + build + e2e + typecheck + lint"
	@echo "  deploy        - Trigger GitHub Pages workflow on main"
	@echo "  deploy-force  - Push empty commit to main to trigger deploy"
	@echo "  prod-url      - Print current production URL"
	@echo "  be-setup      - Create backend venv and install requirements (uv or pip)"
	@echo "  be-run        - Run backend API (uvicorn via uvx or python -m)"
	@echo "  be-test       - Run backend tests (pytest via uvx or python -m)"
	@echo "  be-health     - Curl backend /health"
	@echo "  be-docker-build-dev  - Build backend dev image (reload)"
	@echo "  be-docker-run-dev    - Run backend dev image on :8000"
	@echo "  be-docker-build-prod - Build backend prod image"
	@echo "  be-docker-run-prod   - Run backend prod image on :8000"
	@echo "  compose-up     - docker compose up --build (api+ui)"
	@echo "  compose-down   - docker compose down"

all: build deploy

setup:
	cd $(FRONTEND) && bun install && bunx playwright install chromium

dev:
	cd $(FRONTEND) && bun dev

build:
	cd $(FRONTEND) && bun run build

preview:
	cd $(FRONTEND) && bun run preview --host

test-e2e qa-actions:
	cd $(FRONTEND) && bunx playwright install chromium && bun run test:e2e

qa-live-200:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live.config.ts tests/specs/live-blink.spec.ts

qa-live-100:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live1x.config.ts tests/specs/live-blink-1x.spec.ts

qa-live-caw-200:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live.config.ts tests/specs/live-caw.spec.ts

qa-live-caw-100:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live1x.config.ts tests/specs/live-caw-1x.spec.ts

qa-live-hop-200:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live.config.ts tests/specs/live-hop.spec.ts

qa-live-hop-100:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live1x.config.ts tests/specs/live-hop-1x.spec.ts

qa-live-walk-200:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live.config.ts tests/specs/live-walk.spec.ts

qa-live-walk-100:
	cd $(FRONTEND) && bunx playwright test -c tests/playwright.live1x.config.ts tests/specs/live-walk-1x.spec.ts

typecheck:
	cd $(FRONTEND) && bunx svelte-check

lint:
	cd $(FRONTEND) && bunx prettier --check "**/*.{svelte,js,ts,css,md,json,svg,yml,yaml}"

format:
	cd $(FRONTEND) && bunx prettier --write "**/*.{svelte,js,ts,css,md,json,svg,yml,yaml}"

clean:
	rm -rf $(FRONTEND)/dist $(FRONTEND)/test-results $(FRONTEND)/playwright-report

ci: be-test build test-e2e typecheck lint

deploy:
	gh workflow run $(PAGES_WORKFLOW) --ref main || echo "Use: gh workflow run $(PAGES_WORKFLOW) --ref main"

deploy-force:
	@git rev-parse --abbrev-ref HEAD | grep -q '^main$$' || { echo "Not on main; aborting"; exit 1; }
	git commit --allow-empty -m "chore: trigger pages deploy" && git push origin main

prod-url:
	@echo $(PROD_URL)

# -----------------------------
# Backend tasks
# -----------------------------

be-setup:
	cd $(BACKEND) && (command -v uv >/dev/null 2>&1 \
		&& uv venv .venv && . .venv/bin/activate && uv pip install -r requirements.txt \
		|| ( $$(command -v python3 || echo python) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt ))

be-run:
	cd $(BACKEND) && (command -v uvx >/dev/null 2>&1 \
		&& uvx uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
		|| $$(command -v python3 || echo python) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload)

be-test:
	cd $(BACKEND) && (command -v uvx >/dev/null 2>&1 \
		&& uvx pytest -q \
		|| $$(command -v python3 || echo python) -m pytest -q)

be-health:
	@curl -fsS http://localhost:8000/health | jq . || curl -fsS http://localhost:8000/health || true

# -----------------------------
# Backend Docker / Compose
# -----------------------------

be-docker-build-dev:
	docker build -t corvid-api:dev --target dev $(BACKEND)

be-docker-run-dev:
	docker run --rm -p 8000:8000 corvid-api:dev

be-docker-build-prod:
	docker build -t corvid-api:prod --target prod $(BACKEND)

be-docker-run-prod:
	docker run --rm -p 8000:8000 corvid-api:prod

compose-up:
	docker compose up --build

compose-down:
	docker compose down
