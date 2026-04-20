# Frontend Component Plan — Eye of Horus: Sparks

## Status Key
- [ ] TODO
- [x] DONE
- [~] IN PROGRESS

---

## Layout Components

- [x] **Header** — Logo (WedjatLogo SVG), app title, API status dot
- [x] **Navigation** — iris / oracle / about tabs, active state toggle
- [x] **View Router** — `view-iris`, `view-oracle`, `view-about` visibility switching

---

## Iris Dashboard (`view-iris`)

- [x] **Severity Strip** — sev-0 through sev-3 chips with `.active` toggle
- [x] **Overall Risk Score** — large numeric display + risk level label
- [x] **KPI Grid** — 4 cards: Crowd Density / Weather Risk / Sentiment / Ticket Velocity
- [x] **Signal Breakdown Panel** — 4 `signal-row` items with source + value
- [x] **Auto-Refresh** — 5-second polling via `IrisDashboard._startPolling()`
- [ ] **Event Selector** — dropdown to switch between astroworld/coachella/super_bowl
- [ ] **Risk Trend Sparkline** — 60-second history mini-chart (optional, nice-to-have)
- [ ] **Live Timestamp** — "Last updated: HH:MM:SS" display

---

## Oracle Simulator (`view-oracle`)

- [x] **Scenario Form** — event select, incident type, severity, trigger time inputs
- [x] **Run Simulation Button** — disabled + "Simulating…" state while running
- [x] **Results Panel** — evac time, peak density, at-risk count, injured count
- [x] **Bottleneck List** — location + risk score per bottleneck
- [x] **Recommendations List** — priority, action, location, timing, expected impact
- [ ] **Suggest Scenarios Button** — currently alerts "not implemented"; wire to `/api/oracle/suggest`
- [ ] **Agent Archetype Breakdown** — pie/bar showing casual/influencer/etc distribution
- [ ] **Simulation Progress Bar** — show tick progress during async run (needs WebSocket or SSE)

---

## About View (`view-about`)

- [x] **Backtest Table** — event / risk correct / evac error / accuracy from `/api/sparks/backtest`
- [ ] **Architecture Diagram** — simple SVG or HTML diagram of Iris + Oracle + Sparks flow
- [ ] **Signal Sources Card** — list all 7 sources from `signal_sources.json`
- [ ] **Tech Stack List** — FastAPI · NumPy · Claude · Pydantic

---

## Global

- [x] **CSS Design System** — `#00D4FF` primary, dark theme, severity color vars
- [x] **Severity Animations** — pulseSoft / pulseMed / pulseHard keyframes
- [x] **Responsive Layout** — breakpoints at 1024px and 640px
- [x] **API Client (`api.js`)** — auto localhost vs prod, all 6 endpoints wired
- [ ] **Error Toast** — global error display instead of raw `alert()`
- [ ] **Loading Skeleton** — shimmer placeholder while data loads

---

## Priority for April 21 Demo

**Must Have (P0)**:
1. Event selector on Iris view → switch event context
2. Fix "Suggest Scenarios" button → real API call
3. Live timestamp on Iris refresh

**Nice to Have (P1)**:
4. Error toast system
5. Agent archetype breakdown in Oracle results

**Skip (P2)**:
6. WebSocket progress bar
7. Risk trend sparkline
8. Architecture diagram
