# Eye of Horus: Sparks — Backtesting Plan

## Accuracy Targets by Event

### Astroworld 2024 (NRG Park, Houston)
- **Target**: 92% accuracy on crowd prediction
- **Capacity**: 50,000 (NRG Park festival config)
- **Key Metrics to Hit**:
  - Crowd density peak prediction within ±0.5 persons/sqm
  - Evacuation time estimate within ±10% of actual
  - Risk level classification (CRITICAL) must be correct
  - Bottleneck location: NRG main gate + south tunnel
- **Ground Truth**: Actual attendance ~50,000 · Peak density ~9.2/sqm reported in zone 4 · Event stopped at T+38min
- **Validation Method**: Compare `swarm.run_simulation()` output against `backtest_events_complete.json` ground_truth fields
- **Failure Mode to Avoid**: Underestimating surge speed — model must flag CRITICAL before T+25min

### Coachella 2023 (Empire Polo Club, Indio CA)
- **Target**: 87% accuracy on logistics prediction
- **Capacity**: 125,000 per day
- **Key Metrics to Hit**:
  - Entry flow prediction: main gate queue < 5% deviation
  - Multi-stage density distribution across 7 stages
  - Weather risk score: hot/dry desert conditions must push medical_risk above 0.6
  - Bottleneck: Sahara Stage exit + main entrance re-entry predicted correctly
- **Ground Truth**: Actual ~112,000 attended · 18 medical incidents · Evac time 9 min
- **Validation Method**: `iris/scorer.py` composite score must land in ELEVATED range (0.60–0.79) for peak hours
- **Failure Mode to Avoid**: Missing the Sahara Stage bottleneck — it was the primary logistics failure point

### Super Bowl LVIII (Allegiant Stadium, Las Vegas)
- **Target**: 96% accuracy on entry/exit flow
- **Capacity**: 65,000 (Allegiant Stadium)
- **Key Metrics to Hit**:
  - Entry flow: 61,629 actual attendance prediction within ±3%
  - 8 exit gates must be individually profiled with flow rates
  - Post-game evacuation: 45-minute window prediction within ±5min
  - Security checkpoint throughput modeled per gate
- **Ground Truth**: Actual 61,629 · No major incidents · Normal evacuation ~45min
- **Validation Method**: Bottleneck list must be empty or LOW risk — this is the control event
- **Failure Mode to Avoid**: False positives — system should NOT flag CRITICAL for a well-managed event

---

## Composite Accuracy Target

| Event | Target | Weight | Weighted Score |
|-------|--------|--------|----------------|
| Astroworld 2024 | 92% | 0.40 | 36.8% |
| Coachella 2023 | 87% | 0.35 | 30.5% |
| Super Bowl LVIII | 96% | 0.25 | 24.0% |
| **Overall** | **91.3%** | — | **91.3%** |

**Minimum acceptable for demo**: 88% overall

---

## Test Execution Plan

```bash
# From repo root
source venv/bin/activate
cd backend
python -m pytest tests/ -v --tb=short

# Individual test suites
python -m pytest tests/test_iris.py -v      # Signal scoring
python -m pytest tests/test_oracle.py -v   # Swarm simulation
python -m pytest tests/test_sparks.py -v   # Venue + analytics
```

## Scoring Formula

```
accuracy = 1.0 - (
    0.40 * abs(pred_density - actual_density) / actual_density +
    0.35 * abs(pred_evac_time - actual_evac_time) / actual_evac_time +
    0.25 * (0 if risk_level_correct else 1)
)
```

## Red Lines (Auto-Fail)

1. CRITICAL event (Astroworld) classified as WATCH or NOMINAL → demo failure
2. Safe event (Super Bowl) classified as CRITICAL → false alarm demo failure
3. Evacuation time error > 20% on any event → numeric prediction broken
4. Test suite failure rate > 2/20 tests → backend not demo-ready
