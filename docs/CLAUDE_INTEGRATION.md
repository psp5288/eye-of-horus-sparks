# Claude Integration Guide

## Overview

Claude Opus 4.7 is the reasoning layer of Eye of Horus: Sparks. It powers four integration points that convert raw signal data and simulation outputs into actionable crowd safety intelligence.

**Model**: `claude-opus-4-7`
**Estimated cost**: ~$0.15 per event-hour
**Fallback**: All four functions have rule-based fallbacks — the app works without an API key.

---

## Cost Breakdown

| Integration Point | Calls/Hour | Avg Tokens | Cost/Call | Total/Hour |
|-------------------|-----------|-----------|----------|-----------|
| Agent behavior | 72 (every 50 ticks) | ~500 in / 300 out | $0.002 | $0.144 |
| Signal interpretation | 4 | ~400 in / 200 out | $0.003 | $0.012 |
| Scenario generation | 1 | ~600 in / 400 out | $0.006 | $0.006 |
| Recommendations | 3 | ~700 in / 500 out | $0.005 | $0.015 |
| **Total** | | | | **~$0.177** |

Budget: $500 Anthropic credits → ~2,800 event-hours of operation.

---

## Integration Point 1: Agent Behavior

**File**: `backend/oracle/claude_integration.py`
**Function**: `generate_agent_behavior(agents_sample, environment, history)`
**When called**: Every 50 simulation ticks on a random 10-agent sample

### What it does

During the swarm simulation, Claude decides the immediate behavioral response for each sampled agent based on their archetype, panic level, and the current incident state. This adds AI-driven nuance on top of the NumPy physics engine.

### Example Prompt

```
You are simulating crowd behavior at a live event. Respond ONLY with valid JSON.

Event context:
{
  "venue": "NRG Park",
  "capacity": 50000,
  "incident_type": "crowd_surge",
  "elapsed_time_s": 5400,
  "composite_risk": 0.88
}

For each agent below, decide their immediate behavioral response.

Agents:
[{"id": 1, "archetype": "non_compliant", "x": 45.2, "y": 12.1, "panic_level": 0.3, "state": "moving"}]

Return JSON array:
[{"agent_id": int, "action": str, "speed_modifier": float, "panic_level": float, "direction": str}]
```

### Example Response

```json
[{
  "agent_id": 1,
  "action": "obstruct_flow",
  "speed_modifier": 1.8,
  "panic_level": 0.45,
  "direction": "stage"
}]
```

---

## Integration Point 2: Signal Interpretation

**Function**: `interpret_ambiguous_signals(signal_data, venue_context)`
**When called**: When `composite_risk > 0.60` OR two+ signals contradict

### What it does

When signals disagree (e.g., Twitter shows calm but density is critical), or when risk is elevated, Claude interprets the raw bundle and generates a 2-sentence actionable alert for organizers.

### Example Prompt

```
You are a crowd safety analyst reviewing live event signals. Respond ONLY with valid JSON.

Current signals:
{
  "twitter_sentiment_score": 0.78,
  "twitter_sample": "can't breathe near stage. security doing nothing",
  "crowd_density_score": 0.98,
  "weather_score": 0.05,
  "ticket_velocity_score": 0.85
}

Identify the primary risk driver, any contradictions, and write a 2-sentence alert.

Output JSON:
{"sentiment_label": "calm|rising|agitated|panicked",
 "confidence": float,
 "primary_risk": str,
 "alert": str,
 "confidence_note": str}
```

### Example Response

```json
{
  "sentiment_label": "panicked",
  "confidence": 0.94,
  "primary_risk": "crowd_density_at_stage",
  "alert": "Crowd density at main stage has reached 9.2 persons/m² — above safe limit of 4/m². Immediately dispatch security to create egress corridors and halt new arrivals to the stage area.",
  "confidence_note": "Twitter distress signals corroborate density reading. High confidence."
}
```

---

## Integration Point 3: Scenario Generation

**Function**: `generate_scenarios(event_data, current_state)`
**When called**: On-demand when organizer clicks "Suggest Scenarios". Results cached per `(event_id, event_type)`.

### What it does

Claude generates 3 realistic stress-test scenarios tailored to the specific event — its venue type, crowd profile, and current state.

### Example Response

```json
[
  {
    "name": "South Stage Surge",
    "description": "Surprise artist announcement triggers rush toward south stage during peak attendance.",
    "incident_type": "crowd_surge",
    "trigger_time": 5400,
    "severity": "high",
    "parameters": {"surge_multiplier": 2.2, "origin": "south_stage"}
  },
  {
    "name": "Heat Wave Cluster",
    "description": "Afternoon heat spike to 95°F causes 8+ simultaneous medical incidents near main field.",
    "incident_type": "medical",
    "trigger_time": 14400,
    "severity": "medium",
    "parameters": {"affected_radius_m": 50, "incident_count": 8}
  }
]
```

---

## Integration Point 4: Recommendations

**Function**: `generate_recommendations(predictions, current_state)`
**When called**: Once after each simulation completes

### What it does

Claude converts simulation results into 5 prioritized, specific, actionable recommendations with locations, staffing numbers, and timings.

### Example Response

```json
[
  {
    "priority": 1,
    "action": "Deploy 6 additional security to main stage barrier — create 2m buffer zone immediately",
    "location": "main_stage_barrier",
    "timing": "T+0 (immediately)",
    "expected_impact": "Reduce crowd density from 9.2 to ~5.0 persons/m² within 4 minutes"
  },
  {
    "priority": 2,
    "action": "Open all 4 emergency exit gates on north perimeter",
    "location": "north_perimeter_exits",
    "timing": "Within 60s of incident detection",
    "expected_impact": "Increase exit capacity by 40%, reduce evacuation time from 22min to ~13min"
  }
]
```

---

## Optimization Tips

**Caching**: `generate_scenarios()` results are cached per `(event_id, event_type)` — no repeat calls for same event.

**Batching**: Agent behavior samples 10 agents per call (not one per agent) — 1000x cost reduction vs per-agent calls.

**Fallbacks**: All four functions detect `CLAUDE_API_KEY` absence and fall back to deterministic rule-based logic. Demo mode works without API credits.

**Token efficiency**: Prompts use `Respond ONLY with valid JSON` to eliminate prose and reduce output tokens by ~60%.

---

## Error Handling

```python
# All Claude functions follow this pattern:
raw = await make_claude_call(prompt, max_tokens=1024)
if not raw:
    return _fallback_function(inputs)  # never raises

try:
    return _extract_json(raw)           # strips markdown fences
except Exception:
    return _fallback_function(inputs)   # graceful degradation
```

`make_claude_call()` catches all exceptions and returns `""` — callers always get a usable response.
