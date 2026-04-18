# Claude Integration Guide

## Overview

Claude Opus 4.7 powers four distinct intelligence functions in Eye of Horus: Sparks.

---

## Integration Points

### 1. Agent Behavior Reasoning (`oracle/claude_integration.py`)

**Function**: `generate_agent_behavior(agent, context)`

**When called**: During swarm simulation, every 50 ticks, for a sample of 10 agents.

**Prompt structure**:
```
You are simulating crowd behavior at a live event.

Agent profile:
- Archetype: {archetype}
- Position: {x}, {y} in venue
- Current state: {state}
- Nearby agents: {neighbor_count}
- Incident proximity: {distance_to_incident}m

Event context:
- Venue: {venue_name}, capacity {capacity}
- Incident: {incident_type} at {incident_location}
- Time since incident: {elapsed}s
- Current crowd density: {density}/m²

Based on this profile and context, describe this agent's immediate behavioral response.
Output JSON: {"action": "...", "speed_modifier": 0.0-2.0, "panic_level": 0.0-1.0, "direction": "..."}
```

**Cost optimization**: Only 10 agents sampled per 50 ticks (not all 10,000). Batch 10 agents into one API call using a list prompt.

**Estimated cost**: ~$0.002 per simulation tick batch.

---

### 2. Signal Interpretation (`iris/scorer.py` → `claude_integration.py`)

**Function**: `interpret_signals(signals, threshold)`

**When called**: When composite risk score exceeds 0.6 OR when signals are contradictory (e.g., high Twitter panic but weather is fine).

**Prompt structure**:
```
You are a crowd safety analyst reviewing live event signals.

Current signals:
- Twitter sentiment: {score} ({tweet_count} tweets, sample: "{sample_tweets}")
- Weather risk: {weather_score} ({conditions})
- Crowd density estimate: {density_score} ({estimated_attendance}/{capacity})
- Ticket resale velocity: {resale_score}

Overall risk score: {composite_score}
Confidence: {confidence}%

Identify the primary risk driver, flag any contradictions, and provide a 2-sentence
alert for event organizers. Be specific and actionable.

Output JSON: {"primary_risk": "...", "alert": "...", "confidence_note": "..."}
```

**Cost optimization**: Only triggered when score > 0.6. Cached for 5 minutes (signals don't change that fast).

---

### 3. Scenario Generation (`oracle/scenarios.py` → `claude_integration.py`)

**Function**: `generate_scenarios(event_config, base_scenario)`

**When called**: On-demand when organizer clicks "Suggest Scenarios" in dashboard.

**Prompt structure**:
```
You are a crowd safety consultant preparing stress-test scenarios for a live event.

Event details:
- Venue: {venue_name}, capacity {capacity}
- Event type: {event_type}
- Expected demographics: {demographics}
- Known risks: {known_risks}

Base scenario already configured: {base_scenario_summary}

Generate 3 additional what-if scenarios that would stress-test this event's safety plan.
Focus on: realistic but challenging situations specific to this event type.

Output JSON array: [{"name": "...", "description": "...", "incident_type": "...", 
"trigger_time": 0-3600, "severity": "low|medium|high", "parameters": {...}}]
```

**Cost optimization**: One call per "Suggest Scenarios" click. Results cached per event config.

---

### 4. Recommendations (`oracle/claude_integration.py`)

**Function**: `produce_recommendations(simulation_result, event_config)`

**When called**: After every simulation run completes.

**Prompt structure**:
```
You are a crowd safety expert reviewing simulation results for a live event.

Event: {event_name} at {venue_name}
Simulation scenario: {scenario_name}
Simulation parameters: {agent_count} agents, {duration}s simulated

Key findings:
- Evacuation time: {evacuation_time}s (target: <{target_time}s)
- Bottlenecks: {bottleneck_locations}
- Peak crowd pressure: {max_pressure} agents/m²
- Non-compliant agent impact: {noncompliant_impact}
- Estimated injury risk: {injury_risk}%

Provide 5 specific, actionable recommendations for the event organizer to reduce risk.
Prioritize by impact. Be specific about locations, timing, and staffing numbers.

Output JSON array: [{"priority": 1-5, "action": "...", "location": "...", 
"timing": "...", "expected_impact": "..."}]
```

**Cost optimization**: One call per simulation. Use `max_tokens=1024` — recommendations don't need to be long.

---

## Cost Optimization Strategy

### Per-Event Estimates

| Function | Calls/Hour | Avg Tokens | Cost/Hour |
|----------|-----------|-----------|-----------|
| Agent behavior | 12 (every 5min) | ~800 | ~$0.10 |
| Signal interpretation | 2–4 | ~600 | ~$0.02 |
| Scenario generation | 1 (on-demand) | ~1200 | ~$0.01 |
| Recommendations | 1–3 | ~1000 | ~$0.02 |
| **Total** | | | **~$0.15/hr** |

### With $500 Budget
- **~3,300 hours** of monitoring
- **~10,000 simulation runs**
- More than enough for a hackathon demo + post-event analysis

### Caching Rules
1. Signal interpretation results cached for 5 minutes
2. Scenario suggestions cached per (event_id, scenario_type)
3. Agent behavior responses reused for agents with identical state vectors (within 5% tolerance)

### Prompt Caching
Use Anthropic's prompt caching for the system prompt (event context doesn't change mid-event):
```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": STATIC_SYSTEM_CONTEXT,  # cached
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text", 
                "text": dynamic_prompt  # not cached, changes each call
            }
        ]
    }
]
```

---

## Error Handling

All Claude calls have fallbacks:
- **Timeout (>10s)**: Use rule-based defaults (e.g., panic behavior = move toward nearest exit)
- **API error**: Log, increment error counter, use cached last response
- **Invalid JSON**: Parse with lenient extractor, fall back to text extraction
- **Rate limit**: Exponential backoff, max 3 retries

---

## Model Selection

Using `claude-opus-4-7` (latest as of April 2025) for:
- Nuanced crowd behavior reasoning
- Multi-factor signal interpretation
- Creative scenario generation

For production cost optimization, consider `claude-haiku-4-5` for agent behavior (high-frequency, simpler task) and keep Opus for recommendations and interpretation.
