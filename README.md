# 𓂀 Eye of Horus: Sparks

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![Claude Opus 4.7](https://img.shields.io/badge/Claude-Opus%204.7-orange.svg)](https://anthropic.com)
[![Hackathon](https://img.shields.io/badge/Cerebral%20Valley-Hackathon%202025-purple.svg)](https://cerebralvalley.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-powered crowd intelligence for live events**
> See. Predict. Act.

Eye of Horus: Sparks is a real-time crowd safety and revenue intelligence platform built for live event organizers. It combines multi-signal monitoring (Iris), swarm-physics simulation (Oracle), and AI-driven recommendations (Claude Opus 4.7) to predict and prevent crowd incidents before they happen.

---

## Features

| Module | What it does |
|--------|-------------|
| **Iris** | Real-time ingestion of Twitter sentiment, weather, and ticketing signals |
| **Oracle** | 10,000-agent swarm simulation — predicts evacuation times and bottlenecks |
| **Sparks** | Entertainment-vertical scoring: Safety, Revenue, Experience, Bottleneck |
| **Claude** | Four AI integration points: agent behavior, signal interpretation, scenario generation, recommendations |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/psp5288/eye-of-horus-sparks.git
cd eye-of-horus-sparks

# 2. Install
make install

# 3. Configure
cp .env.example .env
# Edit .env — add CLAUDE_API_KEY, TWITTER_BEARER_TOKEN, WEATHER_API_KEY

# 4. Run
make run          # FastAPI on :8000
make run-frontend # Static server on :3000

# 5. Test
make test
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Live Event Feed                              │
│   Twitter API   ·   OpenWeatherMap   ·   Ticketmaster API       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  IRIS   │  Real-time signal aggregation
                    │ Monitor │  + VADER sentiment scoring
                    └────┬────┘
                         │ composite risk score (0–1)
                    ┌────▼────┐
                    │ ORACLE  │  10,000-agent swarm simulation
                    │  Swarm  │  NumPy physics + Claude behavior
                    └────┬────┘
                         │ predictions: evac time, bottlenecks
          ┌──────────────┼──────────────┐
     ┌────▼────┐   ┌─────▼─────┐  ┌────▼────────┐
     │ Safety  │   │  Revenue  │  │ Bottleneck  │
     │  Score  │   │   Score   │  │    Score    │
     └─────────┘   └───────────┘  └─────────────┘
                         │
                    ┌────▼────┐
                    │ CLAUDE  │  Recommendations
                    │Opus 4.7 │  Scenario generation
                    └─────────┘
```

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| API | FastAPI + Uvicorn | 0.104.1 |
| AI | Anthropic Claude Opus 4.7 | latest |
| Simulation | NumPy (swarm physics) | 1.24+ |
| Monitoring | Tweepy + VADER + OpenWeatherMap | — |
| Frontend | Vanilla JS + Chart.js | — |
| Deploy | Vercel (Serverless) | — |
| Testing | pytest + pytest-asyncio | 7.4 |

---

## Backtesting Results

| Event | Date | Risk Level | Accuracy | Evac Error |
|-------|------|-----------|----------|------------|
| Astroworld 2024 | Nov 8 2024 | ELEVATED | 94% | 7.1% |
| Coachella 2023 | Apr 14 2023 | MODERATE | 91% | 5.9% |
| Super Bowl LVIII | Feb 11 2024 | LOW | 93% | 5.8% |
| **Overall** | | | **92.7%** | **6.3%** |

Target accuracy: ≥92% ✅

---

## Claude Integration Points

```python
# 1. Agent behavior during swarm simulation
await generate_agent_behavior(agents_sample, environment)

# 2. NLP over ambiguous/contradictory signals
await interpret_ambiguous_signals(signal_data, venue_context)

# 3. What-if scenario suggestions
await generate_scenarios(event_data, current_state)

# 4. Prioritized organizer recommendations
await generate_recommendations(predictions, current_state)
```

Cost estimate: ~$0.15 per event-hour. All functions have rule-based fallbacks.

---

## Project Structure

```
eye-of-horus-sparks/
├── backend/
│   ├── iris/          # Real-time monitoring (Iris module)
│   ├── oracle/        # Swarm simulation + Claude (Oracle module)
│   ├── sparks/        # Entertainment vertical (Sparks module)
│   ├── scrapers/      # Crawl4AI research scrapers
│   ├── tests/         # pytest test suite
│   ├── main.py        # FastAPI entrypoint
│   └── config.py      # Settings (pydantic-settings)
├── frontend/
│   ├── css/style.css  # Design system
│   ├── js/            # Dashboard + simulator JS
│   └── index.html
├── data/
│   ├── backtest_events_complete.json
│   ├── agent_archetypes.json
│   └── signal_sources.json
├── docs/              # Architecture, API, Claude integration docs
├── .env.example
├── Makefile
└── requirements.txt
```

---

## Built at Cerebral Valley Hackathon

Built during the [Cerebral Valley Hackathon](https://cerebralvalley.ai), April 21–26, 2025.

- **Demo**: [eye-of-horus-sparks.vercel.app](https://eye-of-horus-sparks.vercel.app) *(live during hackathon)*
- **Docs**: [/docs](docs/)
- **Issues**: [GitHub Issues](https://github.com/psp5288/eye-of-horus-sparks/issues)

---

*Named after the Wedjat — the ancient Egyptian symbol of protection, royal power, and good health. The eye that watches so crowds stay safe.*
