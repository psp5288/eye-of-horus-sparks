# API Documentation

Base URL: `http://localhost:8000` (local) | `https://eye-of-horus-sparks.vercel.app` (prod)

All responses are JSON. All errors follow `{"detail": "message"}`.

---

## GET /api/health

Health check. Returns app info and status.

**Response 200**
```json
{
  "status": "ok",
  "app": "Eye of Horus: Sparks",
  "version": "1.0.0",
  "vertical": "sparks",
  "claude_configured": true,
  "timestamp": "2025-04-21T09:00:00Z"
}
```

---

## GET /api/iris/live-signals

Returns the current aggregated signal bundle for a given event.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | string | yes | Event identifier (e.g. `coachella_2023`) |

**Response 200**
```json
{
  "event_id": "coachella_2023",
  "timestamp": "2025-04-21T09:00:00Z",
  "signals": {
    "twitter": {
      "sentiment_score": 0.35,
      "sample_text": "long lines at north stage but vibe is incredible",
      "tweet_volume": 12400
    },
    "weather": {
      "temperature_f": 87,
      "humidity_pct": 22,
      "conditions": "Partly cloudy",
      "risk_score": 0.18
    },
    "crowd_density": {
      "density_score": 0.72,
      "density_per_sqm": 2.8,
      "hotspots": ["sahara_stage", "main_stage_pit"]
    },
    "ticket_velocity": {
      "velocity_score": 0.55,
      "resale_spike": false,
      "resale_premium_pct": 15
    }
  },
  "composite_risk": 0.42,
  "risk_level": "MODERATE",
  "confidence": 0.81,
  "claude_interpretation": {
    "sentiment_label": "rising",
    "primary_risk": "localized_crowd_pressure",
    "alert": "Minor crowd pressure at Sahara stage. Monitor density near barrier."
  }
}
```

**Error 404**
```json
{"detail": "Event 'unknown_event' not found"}
```

---

## POST /api/oracle/simulate

Run a swarm simulation for a given event and scenario.

**Request Body**
```json
{
  "event_id": "coachella_2023",
  "scenario": {
    "incident_type": "crowd_surge",
    "trigger_time_s": 5400,
    "severity": "high",
    "parameters": {
      "surge_multiplier": 2.0,
      "origin": "sahara_stage"
    }
  },
  "num_agents": 10000,
  "include_claude": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `event_id` | string | required | Event to simulate |
| `scenario` | object | required | Incident scenario |
| `num_agents` | int | 10000 | Agent population size |
| `include_claude` | bool | true | Use Claude for agent behavior |

**Response 200**
```json
{
  "event_id": "coachella_2023",
  "scenario_run_id": "sim_abc123",
  "simulation_time_s": 1.24,
  "predictions": {
    "evacuation_time_seconds": 480,
    "peak_density": 0.78,
    "estimated_injury_risk": 0.12,
    "bottlenecks": [
      {
        "location": "sahara_stage_exit",
        "peak_pressure": 8.4,
        "risk_score": 7.2
      }
    ],
    "agent_outcomes": {
      "safely_evacuated": 9840,
      "at_risk": 160,
      "injured": 18
    },
    "crowd_sentiment_trajectory": [0.35, 0.42, 0.61, 0.74, 0.68, 0.55]
  },
  "scores": {
    "Safety": 72,
    "Revenue": 68,
    "Experience": 75,
    "Bottleneck": 34
  },
  "recommendations": [
    {
      "priority": 1,
      "action": "Deploy 4 staff to Sahara stage exit immediately",
      "location": "sahara_stage_exit",
      "timing": "T+0s",
      "expected_impact": "Reduce evacuation time by ~25%"
    }
  ]
}
```

**Error 422**
```json
{"detail": "Invalid scenario: incident_type must be one of crowd_surge|medical|fire|weather|evacuation|fight"}
```

---

## GET /api/sparks/events

List all configured events with basic risk profiles.

**Response 200**
```json
{
  "events": [
    {
      "event_id": "coachella_2023",
      "event_name": "Coachella Valley Music Festival 2023",
      "date": "2023-04-14",
      "venue": "Empire Polo Club",
      "event_type": "festival",
      "composite_risk": 0.42,
      "risk_level": "MODERATE",
      "scores": {
        "Safety": 72,
        "Revenue": 68,
        "Experience": 75,
        "Bottleneck": 34
      }
    }
  ],
  "total": 3
}
```

---

## GET /api/sparks/events/{event_id}

Full risk profile for a single event.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `event_id` | string | Event identifier |

**Response 200** — includes all fields from `/events` plus:
```json
{
  "factors": {
    "artist_hype_score": 0.85,
    "fan_compliance_estimate": 0.65,
    "alcohol_policy_risk": 0.55,
    "historical_incident_rate": 0.18
  },
  "comparable_events": ["lollapalooza_2022", "astroworld_2024"],
  "risk_adjusted_capacity": 118750,
  "agent_archetypes": {
    "casual": 0.40,
    "friends_group": 0.28,
    "influencer": 0.15,
    "staff": 0.12,
    "non_compliant": 0.05
  }
}
```

**Error 404**
```json
{"detail": "Event 'unknown' not found"}
```

---

## GET /api/sparks/backtest

Returns backtesting accuracy results for all three validation events.

**Response 200**
```json
{
  "overall_accuracy": 0.927,
  "target": 0.92,
  "target_met": true,
  "events": [
    {
      "event_id": "astroworld_2024",
      "risk_level_correct": true,
      "evacuation_time_error_pct": 7.1,
      "bottleneck_locations_correct": true,
      "accuracy": 0.94
    },
    {
      "event_id": "coachella_2023",
      "risk_level_correct": true,
      "evacuation_time_error_pct": 5.9,
      "bottleneck_locations_correct": true,
      "accuracy": 0.91
    },
    {
      "event_id": "super_bowl_58",
      "risk_level_correct": true,
      "evacuation_time_error_pct": 5.8,
      "bottleneck_locations_correct": true,
      "accuracy": 0.93
    }
  ]
}
```
