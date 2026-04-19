# Developer Setup Guide

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.11+ | `python --version` |
| pip | latest | `pip --version` |
| Node.js | 18+ (optional, for npm scripts) | `node --version` |
| Git | any | `git --version` |

---

## 1. Clone

```bash
git clone https://github.com/psp5288/eye-of-horus-sparks.git
cd eye-of-horus-sparks
```

---

## 2. Install Backend

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Or use Make:
```bash
make install-backend
```

---

## 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```bash
# Required for live signals
TWITTER_BEARER_TOKEN=Bearer your_token_here
WEATHER_API_KEY=your_openweathermap_key

# Required for Claude AI features
CLAUDE_API_KEY=sk-ant-your_key_here

# Optional
TICKETMASTER_API_KEY=your_key
```

**Without API keys**: The app runs in fallback mode — all Claude functions use rule-based logic, signals return mock data. Useful for frontend development.

---

## 4. Verify API Connections

```bash
# Test Claude
python -c "from anthropic import Anthropic; c = Anthropic(); print('✓ Anthropic SDK')"

# Test FastAPI imports
python -c "from fastapi import FastAPI; print('✓ FastAPI')"

# Test NumPy (simulation)
python -c "import numpy; print('✓ NumPy', numpy.__version__)"
```

---

## 5. Run Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Or:
```bash
make run
```

API will be live at `http://localhost:8000`.

Swagger docs: `http://localhost:8000/docs`

---

## 6. Run Frontend

```bash
cd frontend
python -m http.server 3000
```

Or:
```bash
make run-frontend
```

Dashboard at `http://localhost:3000`.

---

## 7. Run Both (Parallel)

```bash
make run-all
```

---

## 8. Run Tests

```bash
# All tests
make test

# Individual modules
make test-iris
make test-oracle
make test-sparks

# With coverage
make test-cov
```

---

## 9. Run Backtest Verification

```bash
make backtest
```

This runs the 3-event backtest and reports accuracy. Should show ≥92.7%.

---

## 10. Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy preview
make deploy-preview

# Deploy production
make deploy
```

Ensure `CLAUDE_API_KEY` and other secrets are set in Vercel environment variables:
```
vercel env add CLAUDE_API_KEY
```

---

## Makefile Quick Reference

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make run` | Start FastAPI (port 8000) |
| `make run-frontend` | Start static server (port 3000) |
| `make run-all` | Both in parallel |
| `make test` | Run pytest |
| `make lint` | Run ruff linter |
| `make format` | Run ruff formatter |
| `make health` | Test /api/health endpoint |
| `make backtest` | Run backtest validation |
| `make clean` | Remove __pycache__ |
| `make deploy` | Deploy to Vercel |

---

## Troubleshooting

**`ModuleNotFoundError: crawl4ai`**
```bash
pip install crawl4ai --break-system-packages  # Homebrew Python
python -m playwright install chromium
```

**`CLAUDE_API_KEY not set`**
The app will still run — Claude functions fall back to rule-based logic. Add the key to `.env` when ready.

**Port 8000 already in use**
```bash
lsof -i :8000 | grep LISTEN
kill -9 <PID>
```

**`git push` rejected (divergent branches)**
```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
git push origin main
```
