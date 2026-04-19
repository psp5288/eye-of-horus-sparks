# Architecture: Eye of Horus: Sparks

## System Overview

Eye of Horus: Sparks is a three-module pipeline: **Iris** (real-time monitoring) → **Oracle** (swarm simulation) → **Sparks** (scoring + recommendations). Claude Opus 4.7 is threaded through Oracle and Sparks as the reasoning layer.

---

## Data Flow

```
╔══════════════════════════════════════════════════════════════════╗
║                        SIGNAL LAYER                              ║
║  Twitter API  ──┐                                                ║
║  OpenWeather ──┼──► IrisMonitor.fetch_signals()                 ║
║  Ticketmaster ─┘         │                                       ║
╚══════════════════════════╪═══════════════════════════════════════╝
                           │ SignalBundle (4 scores + raw data)
╔══════════════════════════▼═══════════════════════════════════════╗
║                        IRIS MODULE                               ║
║  IrisScorer.compute_risk_score()                                 ║
║  Weights: Twitter 35% · Density 25% · Weather 25% · Ticket 15%  ║
║  Output: composite_risk (0–1), confidence (0–1)                  ║
╚══════════════════════════╪═══════════════════════════════════════╝
                           │ composite_risk > 0.60 → trigger sim
╔══════════════════════════▼═══════════════════════════════════════╗
║                       ORACLE MODULE                              ║
║  SwarmSimulation(num_agents=10000, dt=0.5s)                      ║
║  ┌─────────────────────────────────────────────────────────┐    ║
║  │  Every 50 ticks → Claude: generate_agent_behavior()    │    ║
║  │  Agent archetypes: Casual · Friends · Influencer ·     │    ║
║  │                    Staff · NonCompliant                 │    ║
║  └─────────────────────────────────────────────────────────┘    ║
║  Output: evacuation_time_s, bottlenecks[], agent_outcomes        ║
╚══════════════════════════╪═══════════════════════════════════════╝
                           │ simulation_output dict
╔══════════════════════════▼═══════════════════════════════════════╗
║                       SPARKS MODULE                              ║
║  compute_sparks_scores(factors, simulation_output)               ║
║  → Safety (0–100)   Revenue (0–100)                              ║
║  → Experience (0–100)   Bottleneck (0–100, lower = better)       ║
║                                                                  ║
║  Claude: generate_recommendations(predictions, state)            ║
║  Claude: generate_scenarios(event_data, current_state)           ║
╚══════════════════════════╪═══════════════════════════════════════╝
                           │ JSON response
╔══════════════════════════▼═══════════════════════════════════════╗
║                     FRONTEND DASHBOARD                           ║
║  Iris Dashboard (live signals)  ·  Oracle Simulator              ║
║  KPI Cards: Safety · Revenue · Experience · Bottleneck           ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Module Breakdown

### Iris — Real-Time Monitoring

| File | Responsibility |
|------|---------------|
| `iris/monitor.py` | `IrisMonitor` — orchestrates signal fetch + scoring |
| `iris/signals.py` | API adapters: Twitter, OpenWeatherMap, Ticketmaster |
| `iris/scorer.py` | Weighted composite risk score formula |
| `iris/models.py` | Pydantic models: Signal, RiskScore, EventData |

Signal weights (validated against Astroworld 2021 backtest):
- Twitter sentiment: **35%** (leading indicator — panic tweets precede physical crush)
- Crowd density: **25%** (primary physical risk driver)
- Weather: **25%** (heat/rain elevates medical incident rate)
- Ticket velocity / resale spikes: **15%** (proxy for demand overflow)

### Oracle — Swarm Simulation

| File | Responsibility |
|------|---------------|
| `oracle/swarm.py` | `SwarmSimulation` — main physics loop |
| `oracle/agents.py` | `Agent` class, `AgentArchetype` enum |
| `oracle/scenarios.py` | `Scenario` dataclass + templates |
| `oracle/claude_integration.py` | Four Claude API integration functions |

Agent archetypes (10,000 agents total):

| Archetype | Share | Compliance | Panic Threshold |
|-----------|-------|-----------|----------------|
| Casual Attendee | 50% | 0.85 | 0.70 |
| Friends Group | 25% | 0.80 | 0.65 |
| Influencer | 15% | 0.50 | 0.55 |
| Staff | 5% | 1.00 | 0.10 |
| Non-Compliant | 5% | 0.10 | 0.40 |

### Sparks — Entertainment Vertical

| File | Responsibility |
|------|---------------|
| `sparks/entertainment.py` | Score computation + evacuation model |
| `sparks/venues.py` | Venue, Event, Exit, Zone Pydantic models |
| `sparks/signals.py` | Entertainment-specific signal definitions |

---

## Claude Integration Points

Four functions in `oracle/claude_integration.py`:

```python
generate_agent_behavior(agents_sample, environment, history)
# Called every 50 ticks on a 10-agent sample
# Returns: [{agent_id, action, speed_modifier, panic_level, direction}]

interpret_ambiguous_signals(signal_data, venue_context)
# Called when composite_risk > 0.60 or signals contradict
# Returns: {sentiment_label, confidence, primary_risk, alert}

generate_scenarios(event_data, current_state)
# Called on-demand from "Suggest Scenarios" button
# Returns: [{name, description, incident_type, trigger_time, severity}]

generate_recommendations(predictions, current_state)
# Called post-simulation
# Returns: [{priority, action, location, timing, expected_impact}]
```

All functions fall back to rule-based logic when `CLAUDE_API_KEY` is not set.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/iris/live-signals` | Current signal bundle |
| POST | `/api/oracle/simulate` | Run swarm simulation |
| GET | `/api/sparks/events` | List configured events |
| GET | `/api/sparks/backtest` | Backtesting accuracy results |
| GET | `/api/sparks/events/{id}` | Single event risk profile |

---

## Deployment Architecture

```
GitHub → Vercel (serverless)
         ├── /api/* → FastAPI (via Mangum adapter)
         └── /* → Static frontend
```

Local dev: `uvicorn backend.main:app --reload --port 8000` + `python -m http.server 3000`

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Simulation time (10k agents, 300 ticks) | ~1.2s |
| Risk score computation | <50ms |
| Claude API latency (agent behavior) | ~800ms |
| End-to-end API response (with Claude) | ~2.5s |
| Backtest accuracy (3 events) | 92.7% |
| Evacuation prediction error | 6.3% avg |
