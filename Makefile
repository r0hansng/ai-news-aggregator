# ==============================================================================
# AI News Aggregator — Makefile
# Usage: make <target>   (run `make help` for a full list)
# ==============================================================================

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
UV        := uv
PYTHON    := $(UV) run python
COMPOSE   := docker compose -f docker/docker-compose.yml
HOURS     ?= 24   # window passed to scrapers / email digest (override: make run HOURS=48)
TOP_N     ?= 10   # top articles in the email digest

.DEFAULT_GOAL := help
.PHONY: help \
        install sync add lock upgrade \
        db-up db-down db-reset db-init db-shell \
        scrape process-anthropic process-youtube \
        digest curator email \
        run run-dry \
        lint format \
        clean

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
help: ## Show this help message
	@echo ""
	@echo "  AI News Aggregator — available targets"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ==============================================================================
# Dependency management (uv)
# ==============================================================================

install: ## Create venv and install all dependencies
	$(UV) venv
	$(UV) sync

sync: ## Sync installed packages to match uv.lock
	$(UV) sync

add: ## Add a new package  (usage: make add PKG=requests)
	$(UV) add $(PKG)

add-dev: ## Add a new dev-only package  (usage: make add-dev PKG=pytest)
	$(UV) add --dev $(PKG)

lock: ## Regenerate uv.lock without installing
	$(UV) lock

upgrade: ## Upgrade all dependencies and refresh uv.lock
	$(UV) lock --upgrade

# ==============================================================================
# Docker / Database lifecycle
# ==============================================================================

db-up: ## Start Postgres + pgAdmin in the background
	$(COMPOSE) up -d
	@echo "  Postgres  → localhost:5432"
	@echo "  pgAdmin   → http://localhost:8080  (admin@local.dev / admin)"

db-down: ## Stop all containers gracefully
	$(COMPOSE) down

db-reset: ## Stop containers AND delete all volumes (destructive!)
	$(COMPOSE) down -v
	@echo "  All data volumes removed."

db-logs: ## Tail Docker container logs
	$(COMPOSE) logs -f

db-init: ## Create database tables (run once after db-up)
	$(PYTHON) -m app.database.create_tables

db-shell: ## Open a psql shell inside the Postgres container
	docker exec -it ai-news-aggregator-db \
		psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-ai_news_aggregator}

# ==============================================================================
# Individual pipeline steps
# ==============================================================================

scrape: ## Step 1 — Scrape YouTube / OpenAI / Anthropic sources
	$(PYTHON) -m app.runner

process-anthropic: ## Step 2 — Convert Anthropic markdown to plain text
	$(PYTHON) -m app.services.process_anthropic

process-youtube: ## Step 3 — Fetch YouTube transcripts
	$(PYTHON) -m app.services.process_youtube

digest: ## Step 4 — Generate AI digests for unprocessed articles
	$(PYTHON) -m app.services.process_digest

curator: ## Step 5 — Rank/curate digests using the curator agent
	$(PYTHON) -m app.services.process_curator

email: ## Step 6 — Build and send the email digest
	$(PYTHON) -m app.services.process_email

# ==============================================================================
# Full pipeline
# ==============================================================================

run: ## Run the complete daily pipeline  (HOURS=24 TOP_N=10 by default)
	$(PYTHON) -m app.daily_runner

run-dry: ## Dry-run: scrape + process only (no digest, no email)
	@echo ">>> [1/3] Scraping..."
	$(PYTHON) -m app.runner
	@echo ">>> [2/3] Processing Anthropic markdown..."
	$(PYTHON) -m app.services.process_anthropic
	@echo ">>> [3/3] Processing YouTube transcripts..."
	$(PYTHON) -m app.services.process_youtube
	@echo ">>> Dry-run complete. No digests or emails were sent."

# ==============================================================================
# Code quality
# ==============================================================================

lint: ## Run ruff linter
	$(UV) run ruff check app/

format: ## Auto-format code with ruff
	$(UV) run ruff format app/

# ==============================================================================
# Housekeeping
# ==============================================================================

clean: ## Remove __pycache__ and .pyc files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "  Cleaned."
