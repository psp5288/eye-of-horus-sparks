# Developer Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ (optional, for frontend tooling)
- Git

## 1. Clone & Structure

```bash
git clone https://github.com/patelparin2005/eye-of-horus-sparks.git
cd eye-of-horus-sparks
```

## 2. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

| Variable | Where to Get |
|----------|-------------|
| `CLAUDE_API_KEY` | https://console.anthropic.com |
| `TWITTER_BEARER_TOKEN` | https://developer.twitter.com |
| `OPENWEATHER_API_KEY` | https://openweathermap.org/api |
| `TICKETMASTER_KEY` | https://developer.ticketmaster.com |

## 4. Run Backend

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Visit:
- Dashboard: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## 5. Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

## 6. Frontend (Development)

The frontend is static HTML/CSS/JS. Just open `frontend/index.html` in a browser,
or serve it with Python:

```bash
cd frontend
python3 -m http.server 3000
# Open http://localhost:3000
```

The frontend JS points to `http://localhost:8000` for API calls. Change `API_BASE_URL`
in `frontend/js/api.js` for production.

## 7. Vercel Deployment

```bash
npm install -g vercel
vercel login
vercel
```

Set environment variables in Vercel dashboard under Project Settings > Environment Variables.

## Troubleshooting

**`ModuleNotFoundError`**: Make sure you're in the activated venv and ran `pip install -r requirements.txt`.

**`Port 8000 already in use`**: Run `lsof -i :8000 | kill -9 PID` or change port in the uvicorn command.

**`CLAUDE_API_KEY not set`**: Check your `.env` file exists and has the correct key name.

**Twitter API 403**: Ensure you have a Twitter Developer account with v2 API access (free tier works).
