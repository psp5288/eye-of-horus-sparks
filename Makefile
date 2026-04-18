# ──────────────────────────────────────────────
#  Eye of Horus: Sparks — Makefile
#  Usage: make <target>
# ──────────────────────────────────────────────

.PHONY: help install install-backend install-frontend run run-frontend test test-iris test-oracle test-sparks lint clean deploy env-check

VENV       := venv
PYTHON     := $(VENV)/bin/python
PIP        := $(VENV)/bin/pip
PYTEST     := $(VENV)/bin/pytest
UVICORN    := $(VENV)/bin/uvicorn
BACKEND    := backend
PORT       := 8000

## help: show this help message
help:
	@echo ""
	@echo "  Eye of Horus: Sparks"
	@echo "  ─────────────────────────────────────"
	@grep -E '^## [a-zA-Z_-]+:' Makefile | awk 'BEGIN {FS = ": "}; {printf "  make %-20s %s\n", $$1, $$2}' | sed 's/## //'
	@echo ""

# ── Setup ──────────────────────────────────────

## install: create venv and install all dependencies
install: install-backend install-frontend
	@echo "✓ All dependencies installed"

install-backend:
	@echo "→ Setting up Python venv..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt
	@echo "✓ Backend dependencies installed"

install-frontend:
	@echo "→ Installing Node dependencies..."
	npm install --silent
	@echo "✓ Frontend dependencies installed"

## env: copy .env.example to .env (safe — won't overwrite existing)
env:
	@if [ ! -f .env ]; then cp .env.example .env && echo "✓ Created .env from .env.example — fill in your API keys"; else echo "  .env already exists (not overwritten)"; fi

# ── Development ────────────────────────────────

## run: start the FastAPI backend server (hot reload)
run: env-check
	@echo "→ Starting FastAPI on http://localhost:$(PORT)"
	@echo "  API docs → http://localhost:$(PORT)/docs"
	cd $(BACKEND) && $(UVICORN) main:app --reload --port $(PORT)

## run-frontend: serve the frontend on port 3000
run-frontend:
	@echo "→ Serving frontend on http://localhost:3000"
	cd frontend && python3 -m http.server 3000

## run-all: start both backend and frontend (requires two terminals or use tmux)
run-all:
	@echo "→ Starting backend + frontend..."
	@echo "  Backend:  http://localhost:$(PORT)"
	@echo "  Frontend: http://localhost:3000"
	@$(MAKE) -j2 run run-frontend

# ── Testing ────────────────────────────────────

## test: run all tests
test:
	cd $(BACKEND) && $(PYTEST) tests/ -v --tb=short

## test-iris: run Iris module tests only
test-iris:
	cd $(BACKEND) && $(PYTEST) tests/test_iris.py -v

## test-oracle: run Oracle module tests only
test-oracle:
	cd $(BACKEND) && $(PYTEST) tests/test_oracle.py -v

## test-sparks: run Sparks module tests only
test-sparks:
	cd $(BACKEND) && $(PYTEST) tests/test_sparks.py -v

## test-cov: run tests with coverage report
test-cov:
	cd $(BACKEND) && $(PYTEST) tests/ --cov=. --cov-report=term-missing -v

# ── Code Quality ───────────────────────────────

## lint: run ruff linter (install with: pip install ruff)
lint:
	@command -v ruff >/dev/null 2>&1 || (echo "  Installing ruff..." && $(PIP) install ruff -q)
	ruff check $(BACKEND)/

## format: auto-format with ruff
format:
	ruff format $(BACKEND)/

# ── Deployment ─────────────────────────────────

## deploy: deploy to Vercel
deploy: env-check
	@command -v vercel >/dev/null 2>&1 || npm install -g vercel
	vercel --prod

## deploy-preview: deploy preview (not production)
deploy-preview:
	vercel

# ── Backtest ───────────────────────────────────

## backtest: run historical backtesting suite
backtest: env-check
	cd $(BACKEND) && $(PYTHON) -c "\
import asyncio, sys; sys.path.insert(0, '.'); \
from oracle.scenarios import run_backtest; \
result = asyncio.run(run_backtest(['astroworld_2021','coachella_2023','superbowl_lviii'], {})); \
print('Overall accuracy:', result['overall_accuracy']); \
print('Target met:', result['target_met'])"

# ── Health Check ───────────────────────────────

## health: check if the API server is running
health:
	@curl -s http://localhost:$(PORT)/api/health | python3 -m json.tool || echo "  Server not running — try: make run"

# ── Cleanup ────────────────────────────────────

## clean: remove generated files (keep .env)
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "✓ Cleaned"

## clean-all: remove venv and node_modules too
clean-all: clean
	rm -rf $(VENV) node_modules
	@echo "✓ Full clean complete"

# ── Guards ─────────────────────────────────────

env-check:
	@if [ ! -f .env ]; then \
		echo "  No .env file found. Run: make env"; \
		echo "  Then fill in your API keys before continuing."; \
		exit 1; \
	fi

# ── Git helpers ────────────────────────────────

## push-docs: add and push documentation files
push-docs:
	git add README.md ARCHITECTURE.md docs/ && \
	git commit -m "docs: update documentation" && \
	git push origin main

## push-backend: add and push backend code
push-backend:
	git add backend/ && \
	git commit -m "feat: update backend modules" && \
	git push origin main

## push-frontend: add and push frontend code
push-frontend:
	git add frontend/ && \
	git commit -m "feat: update frontend dashboard" && \
	git push origin main
