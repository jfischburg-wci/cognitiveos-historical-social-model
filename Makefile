# Root Makefile for common tasks across the repo
# Requires: bun, gh (optional for deploy), playwright browsers

# Variables
FRONTEND := frontend
PROD_URL := https://corvid.contentguru.ai
PAGES_WORKFLOW := pages.yml

.PHONY: help setup dev build preview test-e2e qa-actions qa-live-200 qa-live-100 typecheck lint format clean ci deploy deploy-force prod-url

help:
	@echo "Available targets:"
	@echo "  setup         - Install frontend deps and Playwright browsers"
	@echo "  dev           - Run Vite dev server (frontend)"
	@echo "  build         - Build frontend for production"
	@echo "  preview       - Serve built frontend preview (:4173)"
	@echo "  test-e2e      - Run Playwright e2e suite (local preview)"
	@echo "  qa-actions    - Alias for test-e2e (captures action screenshots)"
	@echo "  qa-live-200   - Capture live blink at 200% zoom"
	@echo "  qa-live-100   - Capture live blink at 100% zoom"
	@echo "  typecheck     - Run svelte-check across Svelte code"
	@echo "  lint          - Prettier check common source files"
	@echo "  format        - Prettier write common source files"
	@echo "  clean         - Remove build/test artifacts"
	@echo "  ci            - Build + test + typecheck + lint"
	@echo "  deploy        - Trigger GitHub Pages workflow on main"
	@echo "  deploy-force  - Push empty commit to main to trigger deploy"
	@echo "  prod-url      - Print current production URL"

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

typecheck:
	cd $(FRONTEND) && bunx svelte-check

lint:
	cd $(FRONTEND) && bunx prettier --check "**/*.{svelte,js,ts,css,md,json,svg,yml,yaml}"

format:
	cd $(FRONTEND) && bunx prettier --write "**/*.{svelte,js,ts,css,md,json,svg,yml,yaml}"

clean:
	rm -rf $(FRONTEND)/dist $(FRONTEND)/test-results $(FRONTEND)/playwright-report

ci: build test-e2e typecheck lint

deploy:
	gh workflow run $(PAGES_WORKFLOW) --ref main || echo "Use: gh workflow run $(PAGES_WORKFLOW) --ref main"

deploy-force:
	@git rev-parse --abbrev-ref HEAD | grep -q '^main$$' || { echo "Not on main; aborting"; exit 1; }
	git commit --allow-empty -m "chore: trigger pages deploy" && git push origin main

prod-url:
	@echo $(PROD_URL)

