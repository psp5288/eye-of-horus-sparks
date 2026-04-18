# API Documentation

Base URL: `http://localhost:8000` (local) | `https://eye-of-horus-sparks.vercel.app` (prod)

All responses are JSON. All endpoints require `Content-Type: application/json` for POST requests.

---

## Health

### `GET /api/health`

Returns service health status.

**Response**:
```json
{
  "status": "healthy",
  "app": "Eye of Horus: Sparks",
  "version": "1.0.0",
  "modules": {
    "iris": "operational",
    "oracle": "operational",
    "sparks": "operational"
  }
}
```

---

## Iris — Real-Time Monitoring

### `GET /api/iris/status`

Returns the current composite risk score and signal breakdown.

**Query Parameters**:
- `event_id` (optional): Filter by event. Defaults to active event.

**Response**:
```json
{
  "event_id": "coachella_2025",
  "timestamp": "2025-04-21T20:00:00Z",
  "risk_score": 0.42,
  "risk_level": "MODERATE",
  "confidence": 0.78,
  "signals": {
    "twitter_sentiment": {
      "score": 0.35,
      "tweet_count": 1247,
      "sample_text": "line is getting crazy at the main stage",
      "trend": "increasing"
    },
    "weather": {
      "score": 0.15,
      "conditions": "Clear, 72°F, 8mph wind",
      "risk_factors": []
    },
    "crowd_density": {
      "score": 0.65,
      "estimated_attendance": 85000,
      "capacity": 100000,
      "density_per_sqm": 2.1
    },
    "ticket_velocity": {
      "score": 0.52,
      "resale_spike": true,
      "walkup_estimate": 3200
    }
  },
  "alert": null,
  "recommendations": []
}
```

**Risk Levels**: `LOW` (0–0.3) | `MODERATE` (0.3–0.6) | `HIGH` (0.6–0.8) | `CRITICAL` (0.8–1.0)

---

### `GET /api/iris/signals`

Returns the raw signal feed for the last N minutes.

**Query Parameters**:
- `minutes` (int, default: 60): How far back to fetch
- `event_id` (optional): Event filter

**Response**:
```json
{
  "event_id": "coachella_2025",
  "window_minutes": 60,
  "signals": [
    {
      "timestamp": "2025-04-21T20:00:00Z",
      "source": "twitter",
      "raw_score": 0.35,
      "data": {...}
    }
  ]
}
```

---

### `POST /api/iris/interpret`

Ask Claude to interpret the current signals and produce a natural language alert.

**Request**:
```json
{
  "event_id": "coachella_2025",
  "force_refresh": false
}
```

**Response**:
```json
{
  "primary_risk": "crowd_density",
  "alert": "Main stage area is approaching critical density (85% capacity). Twitter shows increasing urgency in crowd movement posts. Recommend activating secondary viewing areas and crowd flow staff.",
  "confidence_note": "High confidence — weather clear, 3 concordant signals.",
  "generated_at": "2025-04-21T20:01:15Z",
  "cached": false
}
```

---

## Oracle — Swarm Simulation

### `GET /api/oracle/scenarios`

Returns the list of pre-built and saved scenarios.

**Response**:
```json
{
  "built_in": [
    {
      "id": "concert_general_admission",
      "name": "Concert: General Admission",
      "description": "High-energy GA floor, 10k–25k capacity",
      "incident_types": ["surge", "medical", "weather", "evacuation"]
    },
    {
      "id": "festival_multi_stage",
      "name": "Festival: Multi-Stage",
      "description": "Large outdoor festival with multiple stages",
      "incident_types": ["surge", "fire", "weather", "crowd_crush"]
    },
    {
      "id": "stadium_sports",
      "name": "Stadium: Sports Event",
      "description": "Seated stadium, 50k–80k capacity",
      "incident_types": ["evacuation", "fight", "medical", "fire"]
    }
  ],
  "saved": []
}
```

---

### `POST /api/oracle/simulate`

Run a swarm simulation. This is the core Oracle endpoint.

**Request**:
```json
{
  "scenario_id": "concert_general_admission",
  "event_config": {
    "venue_name": "The Gorge Amphitheatre",
    "capacity": 20000,
    "current_attendance": 18000,
    "crowd_profile": {
      "casual": 0.40,
      "friends_group": 0.30,
      "influencer": 0.10,
      "staff": 0.15,
      "non_compliant": 0.05
    }
  },
  "incident": {
    "type": "crowd_surge",
    "location": "main_stage_pit",
    "trigger_time_seconds": 180,
    "severity": "high"
  },
  "simulation_config": {
    "agent_count": 10000,
    "duration_seconds": 600,
    "use_claude_reasoning": true
  }
}
```

**Response**:
```json
{
  "simulation_id": "sim_abc123",
  "scenario": "concert_general_admission",
  "status": "completed",
  "duration_ms": 12400,
  "results": {
    "evacuation_time_seconds": 847,
    "evacuation_time_formatted": "14 min 7 sec",
    "target_met": false,
    "bottlenecks": [
      {"location": "exit_gate_2", "peak_pressure": 8.2, "time_seconds": 210},
      {"location": "main_entrance", "peak_pressure": 6.1, "time_seconds": 195}
    ],
    "crowd_sentiment_trajectory": [0.6, 0.55, 0.4, 0.2, 0.15, 0.12],
    "peak_density": 9.1,
    "estimated_injury_risk": 0.12,
    "agent_outcomes": {
      "safely_evacuated": 9240,
      "delayed": 620,
      "at_risk": 140
    }
  },
  "recommendations": [
    {
      "priority": 1,
      "action": "Open emergency gates 3 and 4 immediately",
      "location": "North perimeter",
      "timing": "At incident detection (T+0s)",
      "expected_impact": "Reduces evacuation time by ~3 minutes"
    }
  ],
  "visualization_data": {
    "agent_positions_by_tick": "...(compressed)"
  }
}
```

---

### `POST /api/oracle/suggest-scenarios`

Ask Claude to generate what-if scenarios for an event.

**Request**:
```json
{
  "event_config": {
    "venue_name": "Madison Square Garden",
    "capacity": 20000,
    "event_type": "concert",
    "artist": "Taylor Swift",
    "demographics": "18-35, mostly female, high social media engagement"
  }
}
```

**Response**:
```json
{
  "scenarios": [
    {
      "name": "Social Media Surge",
      "description": "Influencer posts go viral mid-show, causing unexpected crowd movement toward stage",
      "incident_type": "crowd_surge",
      "trigger_time": 3600,
      "severity": "medium",
      "parameters": {"social_multiplier": 2.5}
    }
  ]
}
```

---

## Sparks — Entertainment Events

### `GET /api/sparks/events`

Returns configured events.

**Response**:
```json
{
  "events": [
    {
      "id": "coachella_2025_w1",
      "name": "Coachella 2025 - Weekend 1",
      "venue": "Empire Polo Club",
      "capacity": 125000,
      "date": "2025-04-18",
      "status": "active"
    }
  ]
}
```

---

### `GET /api/sparks/events/{event_id}/risk-profile`

Returns entertainment-specific risk profile for an event.

**Response**:
```json
{
  "event_id": "coachella_2025_w1",
  "entertainment_score": 0.72,
  "factors": {
    "artist_hype_score": 0.85,
    "fan_compliance_estimate": 0.70,
    "alcohol_policy_risk": 0.45,
    "historical_incident_rate": 0.12
  },
  "comparable_events": ["coachella_2023", "lollapalooza_2022"],
  "risk_adjusted_capacity": 108000
}
```

---

## Backtesting

### `POST /api/backtest/run`

Run backtesting against historical event data.

**Request**:
```json
{
  "event_ids": ["astroworld_2021", "coachella_2023", "superbowl_lviii"],
  "simulation_config": {
    "agent_count": 10000,
    "use_claude_reasoning": false
  }
}
```

**Response**:
```json
{
  "backtest_id": "bt_xyz789",
  "results": [
    {
      "event_id": "astroworld_2021",
      "predicted_risk_score": 0.89,
      "actual_risk_level": "CRITICAL",
      "accuracy": 0.94,
      "predicted_evacuation_time": 1240,
      "actual_casualties": 10,
      "model_assessment": "correctly flagged critical density"
    }
  ],
  "overall_accuracy": 0.926,
  "target_met": true
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "simulation_timeout",
  "message": "Simulation exceeded 60s limit. Try reducing agent_count.",
  "code": 408
}
```

Common error codes:
- `400` — Invalid request parameters
- `404` — Event or scenario not found
- `408` — Simulation timeout
- `429` — Claude API rate limit hit
- `500` — Internal server error
