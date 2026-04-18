# Architecture: Eye of Horus: Sparks

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Event Organizer                          │
│                    (Web Dashboard)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                            │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐  │
│  │    IRIS     │  │   ORACLE    │  │      SPARKS        │  │
│  │ (Monitoring)│  │ (Simulation)│  │  (Entertainment)   │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬───────────┘  │
│         │                │                   │              │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │              Claude Opus 4.7 Integration             │   │
│  │  - Agent Reasoning  - Signal Interpretation          │   │
│  │  - Scenario Generation  - Recommendations            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                │                   │
┌────────▼───┐   ┌────────▼───┐   ┌──────────▼──────┐
│  Twitter   │   │  Weather   │   │  Ticketmaster    │
│  API v2    │   │    API     │   │      API         │
└────────────┘   └────────────┘   └─────────────────┘
```

---

## Module Architecture

### Iris (Real-Time Monitoring)

**Responsibility**: Ingest external signals, aggregate, and produce a composite risk score.

```
External APIs
     │
     ▼
signals.py (Ingestion Layer)
  - TwitterSignal: fetch recent tweets, run sentiment
  - WeatherSignal: fetch conditions, compute weather risk
  - TicketingSignal: estimate crowd density from sales
     │
     ▼
monitor.py (Aggregation Layer)
  - IrisMonitor.collect_all_signals()
  - Parallel signal collection
  - Caches last-known values on API failure
     │
     ▼
scorer.py (Risk Layer)
  - RiskScorer.compute_risk_score()
  - Weighted composite: sentiment(0.35) + weather(0.25) + density(0.25) + velocity(0.15)
  - Confidence interval from signal agreement
     │
     ▼
models.py (Output)
  - RiskLevel enum: LOW / MODERATE / HIGH / CRITICAL
  - IrisStatus dataclass (score, confidence, signals, recommendations)
```

### Oracle (Swarm Simulation)

**Responsibility**: Run 10,000-agent simulation of crowd behavior for a given scenario.

```
scenarios.py (Scenario Setup)
  - EventScenario: venue layout, entry points, capacity, crowd profile
  - Pre-built: concert_general_admission, festival_main_stage, stadium_sports
     │
     ▼
agents.py (Agent Definitions)
  - 5 archetypes: Casual, FriendsGroup, Influencer, Staff, NonCompliant
  - Each archetype: speed, compliance, panic_threshold, social_influence
     │
     ▼
swarm.py (Simulation Engine)
  - SwarmSimulation: initializes N agents on venue grid
  - Tick-based: each tick = 1 second of real time
  - Physics: position update, collision, crowd pressure
  - Events: trigger_incident(), trigger_evacuation()
     │
     ▼
claude_integration.py (AI Layer)
  - generate_agent_behavior(): Claude reasons about archetype response
  - interpret_signals(): Claude reads ambiguous risk indicators
  - generate_scenarios(): Claude suggests what-if variants
  - produce_recommendations(): Claude outputs organizer guidance
     │
     ▼
SimulationResult
  - evacuation_time_seconds, bottleneck_locations
  - casualty_risk_score, crowd_sentiment_trajectory
  - recommendations[]
```

### Sparks (Entertainment Vertical)

**Responsibility**: Event-specific scoring and venue/artist data models.

```
venues.py   → Venue, EventConfig, CrowdProfile
entertainment.py → EntertainmentScorer (artist hype, fan demographics, alcohol policy)
signals.py  → SocialBuzzSignal, TicketResaleSignal, ArtistAnnouncementSignal
```

---

## Data Flow: Live Event Monitoring

```
1. Event organizer opens dashboard
2. Frontend polls GET /api/iris/status every 30s
3. IrisMonitor.collect_all_signals() runs in parallel:
   - Twitter API → 100 recent tweets → VADER sentiment → score 0–1
   - OpenWeatherMap → conditions → weather risk model → score 0–1
   - Ticketmaster → sales velocity → density estimate → score 0–1
4. RiskScorer computes weighted composite
5. If score > 0.7: Claude interprets signals → natural language alert
6. Response returned to dashboard
7. Dashboard updates gauge, signal bars, recommendation panel
```

## Data Flow: Swarm Simulation

```
1. Organizer configures scenario (venue, capacity, incident type)
2. POST /api/oracle/simulate
3. SwarmSimulation initialized:
   - 10,000 agents placed on venue grid
   - Archetypes distributed per crowd profile
4. Simulation runs for N ticks (configurable, default 600 = 10 min)
5. Every 50 ticks: Claude generates behavior modifiers for 10 sampled agents
6. Incident triggered at tick T_incident
7. Simulation records: positions, pressures, evacuation state
8. SimulationResult aggregated
9. Claude produces final recommendations
10. Result returned with visualization data
```

---

## Deployment Architecture (Vercel)

```
Vercel Project
├── /api/* → Python serverless functions (FastAPI via Mangum)
└── /      → Static frontend (index.html, CSS, JS)

Environment Variables (set in Vercel dashboard):
  CLAUDE_API_KEY, TWITTER_BEARER_TOKEN, OPENWEATHER_API_KEY, TICKETMASTER_KEY
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Risk score refresh | < 30s |
| Simulation (10k agents, 600 ticks) | < 45s |
| API response (dashboard) | < 500ms |
| Backtesting accuracy | ≥ 92% |
| Claude API cost per simulation | < $0.05 |
