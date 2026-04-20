# April 21 Execution Schedule — Eye of Horus: Sparks

## Goal: Live demo-ready by end of day

---

## Hour 0–1 (09:00–10:00): Backend Boot

| Time | Task | Owner | Done? |
|------|------|-------|-------|
| 09:00 | `git pull origin main` — get latest | Dev | [ ] |
| 09:05 | `source venv/bin/activate` | Dev | [ ] |
| 09:10 | `cd backend && uvicorn main:app --reload` | Dev | [ ] |
| 09:15 | Hit `GET /api/health` → confirm `{"status":"ok"}` | Dev | [ ] |
| 09:20 | Hit `GET /api/iris/live-signals?event_id=coachella_2023` | Dev | [ ] |
| 09:30 | Hit `POST /api/oracle/simulate` with coachella payload | Dev | [ ] |
| 09:45 | Add `CLAUDE_API_KEY` to `.env` if key available | Dev | [ ] |
| 10:00 | Run `pytest tests/ -v` → must be 21/21 green | Dev | [ ] |

---

## Hour 1–2 (10:00–11:00): Frontend Wiring

| Time | Task | Done? |
|------|------|-------|
| 10:00 | Open `frontend/index.html` in browser | [ ] |
| 10:05 | Verify API status dot goes GREEN | [ ] |
| 10:15 | Navigate to Iris view → KPI cards load | [ ] |
| 10:25 | Add event selector dropdown to Iris view | [ ] |
| 10:40 | Wire event selector → `EohAPI.getLiveSignals(eventId)` | [ ] |
| 10:50 | Add live timestamp "Last updated: HH:MM:SS" | [ ] |

---

## Hour 2–3 (11:00–12:00): Oracle Simulator

| Time | Task | Done? |
|------|------|-------|
| 11:00 | Run sim: coachella_2023 + crowd_surge + high | [ ] |
| 11:10 | Verify bottleneck list renders correctly | [ ] |
| 11:20 | Verify recommendations render with priority numbers | [ ] |
| 11:30 | Fix "Suggest Scenarios" button → call `/api/oracle/suggest` | [ ] |
| 11:45 | Test all 3 events × 3 incident types (9 combos) | [ ] |
| 12:00 | Run Astroworld sim → confirm CRITICAL risk level returned | [ ] |

---

## Hour 3–4 (12:00–13:00): Lunch + Buffer

- Break or fix bugs found in Hour 2–3
- Commit all changes: `git commit -m "April 21 wiring complete"`

---

## Hour 4–5 (13:00–14:00): Claude Integration

| Time | Task | Done? |
|------|------|-------|
| 13:00 | If API key available: test real Claude response for one sim | [ ] |
| 13:15 | Verify fallback works with no key (mock responses) | [ ] |
| 13:30 | `generate_recommendations()` output appears in UI | [ ] |
| 13:45 | `generate_scenarios()` populates suggest panel | [ ] |

---

## Hour 5–6 (14:00–15:00): Backtesting Validation

| Time | Task | Done? |
|------|------|-------|
| 14:00 | Run coachella sim → compare to ground_truth in JSON | [ ] |
| 14:15 | Check: accuracy ≥ 87% (coachella target) | [ ] |
| 14:30 | Run super_bowl sim → confirm no CRITICAL false alarm | [ ] |
| 14:45 | Run astroworld sim → confirm CRITICAL classification | [ ] |
| 15:00 | Accuracy meets 88% composite minimum → DEMO READY | [ ] |

---

## Hour 6–7 (15:00–16:00): Polish + Error Handling

| Time | Task | Done? |
|------|------|-------|
| 15:00 | Replace `alert()` calls with inline error messages | [ ] |
| 15:20 | Loading state during simulation (disable button + spinner) | [ ] |
| 15:40 | About view backtest table loads correctly | [ ] |
| 16:00 | Final `git push origin main` | [ ] |

---

## Hour 7–8 (16:00–17:00): Demo Rehearsal

| Time | Task | Done? |
|------|------|-------|
| 16:00 | Full demo run-through: Iris → Oracle → About | [ ] |
| 16:20 | Time the flow: target < 3 minutes for core demo | [ ] |
| 16:40 | Prepare talking points for each module | [ ] |
| 17:00 | DONE — repo frozen for submission | [ ] |

---

## Demo Script (3-minute version)

1. **Open Iris view** → "Real-time signal aggregation — 4 sources, 5-second refresh"
2. **Switch to Astroworld event** → severity strip goes CRITICAL → "System flagged this 20 minutes before NRG Park reached critical density"
3. **Open Oracle view** → run coachella_2023 / crowd_surge / high → "10,000-agent swarm simulation powered by NumPy physics"
4. **Show recommendations** → "Claude interprets the simulation and generates actionable interventions"
5. **About view** → backtest table → "92% accuracy on Astroworld, 87% on Coachella"

---

## Emergency Fallbacks

| Problem | Fallback |
|---------|----------|
| Backend won't start | Use `python -m uvicorn main:app` instead |
| Claude API fails | Mocks are production-quality — demo works without key |
| Port 8000 blocked | `uvicorn main:app --port 8080` + update `api.js` BASE_URL |
| Test failures | Run single file `pytest tests/test_iris.py -v` to isolate |
| Frontend blank | Check browser console — likely CORS on API calls |
