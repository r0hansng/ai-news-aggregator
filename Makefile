# ==============================================================================
# AI News Aggregator — Global Orchestration
# 
# Design Philosophy:
# - Self-Documenting: Use `make help` to discover all operational targets.
# - Tooling-Agnostic: Abstracts complex `uv`, `bun`, and `docker` commands.
# - Context-Aware: Managed through specific project flags (--project, --reload-dir).
# ==============================================================================

# ---------------------------------------------------------------------------
# Configuration & Binary Paths
# ---------------------------------------------------------------------------
UV        := uv
PYTHON    := $(UV) --project backend run python
COMPOSE   := docker compose -f docker/docker-compose.yml
HOURS     ?= 168  # Processing window (override: make run HOURS=48)
TOP_N     ?= 10   # Quantity of signals in email (override: make run TOP_N=5)

.DEFAULT_GOAL := help
.PHONY: help \
        install sync add lock upgrade \
        db-up db-down db-reset db-migrate db-history db-shell \
        redis-cli redis-flush \
        fe-install fe-dev \
        scrape process-anthropic process-youtube \
        digest curator email \
        run run-dry \
        test test-backend test-frontend test-e2e \
        lint format \
        clean

# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------
help: ## Discovery: Show all available operational targets
	@echo ""
	@echo "  AI News Aggregator — Production Orchestration"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ==============================================================================
# Backend Dependency Management (uv)
# ==============================================================================

install: ## Setup: Create virtualenv and install all backend dependencies
	$(UV) venv backend/.venv
	$(UV) --project backend sync

sync: ## Maintenance: Force sync installed packages to match lockfile
	$(UV) --project backend sync

add: ## Lifecycle: Add new production package (usage: make add PKG=requests)
	$(UV) --project backend add $(PKG)

add-dev: ## Lifecycle: Add new development package (usage: make add-dev PKG=pytest)
	$(UV) --project backend add --dev $(PKG)

lock: ## Manifest: Regenerate backend lockfile (uv.lock)
	$(UV) --project backend lock

upgrade: ## Security: Upgrade all backend dependencies to latest versions
	$(UV) --project backend lock --upgrade

# ==============================================================================
# Docker & Database Lifecycle
# ==============================================================================

db-up: ## Infra: Provision Postgres and pgAdmin containers (background)
	$(COMPOSE) up -d
	@echo "  Local Postgres → localhost:5432"
	@echo "  Admin Dashboard → http://localhost:8080 (admin@local.dev / admin)"

db-down: ## Infra: Gracefully terminate all service containers
	$(COMPOSE) down

db-reset: ## Maintenance: Terminate services AND purge all volumes (destructive)
	$(COMPOSE) down -v
	@echo "  System state fully purged."

db-logs: ## Debug: Stream real-time container logs to terminal
	$(COMPOSE) logs -f

db-migrate: ## Migration: Apply all pending database schema updates (Alembic)
	cd backend && export DATABASE_URL="postgresql://$${POSTGRES_USER:-postgres}:$${POSTGRES_PASSWORD:-postgres}@localhost:$${POSTGRES_PORT:-5432}/$${POSTGRES_DB:-ai_news_aggregator}" && $(UV) run alembic upgrade head

db-history: ## Migration: Show all database version history
	cd backend && $(UV) run alembic history --verbose

db-init: db-migrate ## Bootstrap: Initialize schema and stamp version (first run)
	@echo "  Database schema fully synchronized."

db-shell: ## Access: Enter interactive psql shell inside the container
	docker exec -it ai-news-aggregator-db \
		psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-ai_news_aggregator}

# ==============================================================================
# Cache Management (Redis)
# ==============================================================================

redis-cli: ## Access: Open interactive Redis CLI
	docker exec -it ai-news-aggregator-cache redis-cli

redis-flush: ## Maintenance: Purge all cached data (all users)
	docker exec -it ai-news-aggregator-cache redis-cli flushall
	@echo "  Cache successfully purged."

# ==============================================================================
# Frontend Orchestration (Bun)
# ==============================================================================

fe-install: ## Setup: Install frontend dependencies using Bun
	cd frontend && bun install

fe-dev: ## Development: Launch Next.js dev server (localhost:3000)
	cd frontend && bun run dev

# ==============================================================================
# Technical Signal Pipeline (Step-by-Step)
# ==============================================================================

scrape: ## Step 1: Execute primary source scrapers (YT/API)
	$(PYTHON) -m backend.cmd.worker

process-anthropic: ## Step 2: Normalize Anthropic research signals
	$(PYTHON) -m backend.features.signals.process_anthropic

process-youtube: ## Step 3: Extract and process YouTube technical transcripts
	$(PYTHON) -m backend.features.signals.process_youtube

digest: ## Step 4: Synthesize raw signals into AI-generated digests
	$(PYTHON) -m backend.features.digests.process_digest

curator: ## Step 5: Rank signals via Curator Agent (Llama 3.3)
	$(PYTHON) -m backend.features.digests.process_curator

email: ## Step 6: Dispatch curated signals via email delivery engine
	$(PYTHON) -m backend.features.digests.process_email

# ==============================================================================
# Integrated Workflow
# ==============================================================================

run: ## Production: Execute the comprehensive daily signal pipeline (Synchronous)
	$(PYTHON) -m backend.cmd.daily_worker $(HOURS) $(TOP_N)

run-async: ## Production: Execute the distributed signal pipeline (Celery)
	$(PYTHON) -m backend.cmd.async_daily_worker $(HOURS) $(TOP_N)

run-dry: ## Validation: Execute scraping and processing only (no delivery)
	@echo ">>> [1/3] Triggering Signal Scrapers..."
	$(PYTHON) -m backend.cmd.worker
	@echo ">>> [2/3] Normalizing Research Signals..."
	$(PYTHON) -m backend.features.signals.process_anthropic
	@echo ">>> [3/3] Processing Video Transcripts..."
	$(PYTHON) -m backend.features.signals.process_youtube
	@echo ">>> Dry-run complete. System state updated; no digests emitted."

# ==============================================================================
# Code Quality & Standards
# ==============================================================================

lint: ## Quality: Audit code for style and logical errors (Ruff)
	$(UV) --project backend run ruff check backend/

format: ## Quality: Auto-enforce standard code formatting (Ruff)
	$(UV) --project backend run ruff format backend/

# ==============================================================================
# Testing & Validation
# ==============================================================================

test-backend: ## Test: Run backend unit and integration tests
	PYTHONPATH=. $(UV) --project backend run pytest backend/tests

test-frontend: ## Test: Run frontend logic tests (Vitest)
	cd frontend && bun x vitest run

test-e2e: ## Test: Run Playwright E2E tests (requires dev server)
	cd frontend && npx playwright test

test: test-backend test-frontend ## Test: Run all backend and frontend unit tests

# ==============================================================================
# System Housekeeping
# ==============================================================================

clean: ## Maintenance: Purge cache artifacts and temporary binaries
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "  Artifacts purged."
