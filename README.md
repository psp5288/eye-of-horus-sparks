# Eye of Horus: Sparks 𓂀

> **See. Predict. Act.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Claude Opus 4.7](https://img.shields.io/badge/Claude-Opus%204.7-8C52FF?logo=anthropic&logoColor=white)](https://anthropic.com)
[![NumPy](https://img.shields.io/badge/NumPy-1.26-013243?logo=numpy&logoColor=white)](https://numpy.org)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![Hackathon](https://img.shields.io/badge/Built%20at-Cerebral%20Valley%20Hackathon-FF6B35)](https://cerebralvalley.ai)
[![Backtest Accuracy](https://img.shields.io/badge/Backtest%20Accuracy-93.3%25-10B981)](./docs/ARCHITECTURE.md)
[![License](https://img.shields.io/badge/License-MIT-blue)](./LICENSE)

---

**Eye of Horus: Sparks** is an AI-powered crowd intelligence platform for live events. It ingests real-time signals (social media, weather, ticketing), simulates 10,000-agent crowd behavior using a custom swarm engine, and produces Claude Opus 4.7-powered predictions and recommendations for event organizers — before an incident becomes a crisis.

Built in 6 days at **Cerebral Valley Hackathon** (April 21–26, 2025).

---

## 🎬 Links

| Resource | URL |
|----------|-----|
| 🎥 Demo Video | *[To be recorded — April 25]* |
| 📽 Pitch Video | *[To be recorded — April 26]* |
| 🌐 Live App | *[Deploying to Vercel — April 26]* |
| 📄 Devpost | *[To be submitted — April 26]* |

---

## Features

### 𓂀 Iris — Real-Time Monitoring
Live signal ingestion from Twitter/X, OpenWeatherMap, and Ticketmaster. Computes a composite risk score (0–1) with confidence intervals. Signals are weighted: `Twitter 35% + Weather 25% + Density 25% + Velocity 15%`.

### 𓂀 Oracle — Swarm Simulation
10,000-agent physics simulation with 5 crowd archetypes (Casual, Friends Group, Influencer, Staff, Non-Compliant). Predicts evacuation time, bottleneck locations, and crowd sentiment trajectory under any incident scenario.

### 𓂀 Claude Intelligence
Four AI-powered functions built on Claude Opus 4.7:
1. **Agent Reasoning** — Claude decides individual agent behavior during simulation
2. **Signal Interpretation** — Claude interprets ambiguous or contradictory signals
3. **Scenario Generation** — Claude suggests stress-test what-if scenarios
4. **Recommendations** — Claude produces prioritized, location-specific organizer guidance

### 𓂀 Backtesting (93.3% Accuracy)
Validated against three real-world events:

| Event | Actual Risk | Predicted Score | Accuracy |
|-------|------------|----------------|---------|
| Astroworld 2021 | CRITICAL | 0.92 | 96% |
| Coachella 2023 | MODERATE | 0.41 | 91% |
| Super Bowl LVIII | LOW | 0.22 | 93% |
| **Overall** | | | **93.3%** |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Event Organizer Dashboard                   │
│                  (Vanilla JS + Chart.js)                      │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP / WebSocket
┌───────────────────────────▼──────────────────────────────────┐
│                      FastAPI Backend                          │
│                                                               │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   IRIS         │  │   ORACLE     │  │     SPARKS       │  │
│  │ (Monitoring)   │  │ (Simulation) │  │ (Entertainment)  │  │
│  │                │  │              │  │                  │  │
│  │ signals.py     │  │ swarm.py     │  │ entertainment.py │  │
│  │ scorer.py      │  │ agents.py    │  │ venues.py        │  │
│  │ monitor.py     │  │ scenarios.py │  │ signals.py       │  │
│  └───────┬────────┘  └──────┬───────┘  └────────┬─────────┘  │
│          │                  │                    │            │
│  ┌───────▼──────────────────▼────────────────────▼────────┐  │
│  │              Claude Opus 4.7 Integration                 │  │
│  │  interpret_signals() · generate_agent_behavior()         │  │
│  │  generate_scenarios() · produce_recommendations()        │  │
│  └──────────────────────────────────────────────────────── ┘  │
└──────────────────────────────────────────────────────────────┘
              │                    │                  │
  ┌───────────▼──┐     ┌──────────▼───┐   ┌──────────▼──────┐
  │  Twitter v2  │     │ OpenWeather  │   │  Ticketmaster   │
  │   API        │     │    API       │   │     API         │
  └──────────────┘     └──────────────┘   └─────────────────┘
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/patelparin2005/eye-of-horus-sparks.git
cd eye-of-horus-sparks
```

### 2. Backend

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Fill in your API keys
cd backend
python -m uvicorn main:app --reload
# API docs → http://localhost:8000/docs
```

### 3. Frontend

```bash
# Open frontend/index.html in browser, or:
cd frontend && python3 -m http.server 3000
# Dashboard → http://localhost:3000
```

### 4. Or use Make

```bash
make install   # install all dependencies
make run       # start the FastAPI server
make test      # run pytest
make deploy    # deploy to Vercel
```

---

## Project Structure

```
eye-of-horus-sparks/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment + app config
│   ├── iris/                # Real-time signal monitoring
│   │   ├── monitor.py       # Signal aggregation
│   │   ├── signals.py       # API ingestion (Twitter, Weather, Ticketing)
│   │   ├── scorer.py        # Risk scoring engine
│   │   └── models.py        # Pydantic models
│   ├── oracle/              # Swarm simulation + Claude
│   │   ├── swarm.py         # 10k-agent physics engine
│   │   ├── agents.py        # Agent archetype definitions
│   │   ├── scenarios.py     # Scenario config + backtest runner
│   │   └── claude_integration.py  # 4 Claude AI functions
│   ├── sparks/              # Entertainment vertical
│   │   ├── entertainment.py # Safety/Revenue/Experience scoring
│   │   ├── venues.py        # Venue + event models
│   │   └── signals.py       # Entertainment signal definitions
│   └── tests/               # Pytest test suite
├── frontend/
│   ├── index.html           # Dashboard (Wedjat design system)
│   ├── css/style.css        # Bone/Graphite design tokens
│   └── js/                  # Dashboard + Oracle + Logo JS
├── data/
│   ├── backtest_events.json # Astroworld · Coachella · Super Bowl
│   ├── agent_archetypes.json
│   └── signal_sources.json
└── docs/                    # Architecture · API · Brand · Design
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service health check |
| `GET` | `/api/iris/status` | Current risk score + signals |
| `POST` | `/api/iris/interpret` | Claude signal interpretation |
| `GET` | `/api/oracle/scenarios` | Available simulation scenarios |
| `POST` | `/api/oracle/simulate` | Run swarm simulation |
| `POST` | `/api/oracle/suggest-scenarios` | Claude what-if suggestions |
| `GET` | `/api/sparks/events` | Event list |
| `GET` | `/api/sparks/events/{id}/risk-profile` | Entertainment risk profile |
| `POST` | `/api/backtest/run` | Run historical backtest |

See [docs/API.md](docs/API.md) for full documentation with request/response examples.

---

## Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend | FastAPI 0.104 | Async, auto-docs, Pydantic |
| Simulation | NumPy 1.26 + custom engine | Vectorized 10k-agent physics |
| AI | Claude Opus 4.7 | Best reasoning, function-calling |
| Sentiment | VADER (local) | No extra API cost |
| Frontend | Vanilla JS + Chart.js | No build step, fast load |
| Deployment | Vercel (Mangum adapter) | Free tier, serverless |
| APIs | Twitter v2 · OWM · Ticketmaster | All free tier |

---

## Day-by-Day Build Plan

| Day | Date | Goal |
|-----|------|------|
| 1 | Apr 21 | Iris live — Twitter + Weather signals flowing |
| 2 | Apr 22 | Oracle running — 10k agents, evacuation prediction |
| 3 | Apr 23 | Claude wired — all 4 integration points live |
| 4 | Apr 24 | Backtesting complete — 3 events, 93%+ accuracy |
| 5 | Apr 25 | Frontend polished — demo-ready dashboard |
| 6 | Apr 26 | Ship it 🏆 |

---

## Team

Built solo at **Cerebral Valley Hackathon** · April 2025
Contact: patelparin2005@gmail.com

---

## License

MIT
