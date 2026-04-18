"""
Claude Opus 4.7 integration for Eye of Horus: Sparks.

Four integration points:
  1. generate_agent_behavior()  — agent reasoning during swarm simulation
  2. interpret_ambiguous_signals() — NLP over contradictory signal data
  3. generate_scenarios()       — what-if scenario suggestions
  4. generate_recommendations() — prioritized organizer guidance

All functions have rule-based fallbacks so the app works without API keys
(useful for local dev and demos when API budget needs preserving).

Cost estimate per event-hour: ~$0.15
  - Agent behavior:   12 calls × $0.002  = $0.024
  - Signal interp:    4  calls × $0.003  = $0.012
  - Scenario gen:     1  call  × $0.006  = $0.006
  - Recommendations:  3  calls × $0.005  = $0.015
  - Buffer:                                $0.093
"""

import json
import asyncio
import logging
from typing import Optional

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client = None


def _get_client():
    """Return a shared Anthropic client (lazy-initialised)."""
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic(api_key=settings.claude_api_key)
    return _client


def _extract_json(text: str) -> dict | list:
    """Extract JSON from Claude response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


async def make_claude_call(prompt: str, max_tokens: int = 1024) -> str:
    """
    Wrapper around the Anthropic Messages API.

    Parameters
    ----------
    prompt : str
        The full prompt to send to Claude.
    max_tokens : int
        Maximum tokens in the response (default 1024).

    Returns
    -------
    str
        Claude's response text, or an empty string on error.

    Raises
    ------
    Does NOT raise — catches all exceptions and returns "" so callers can
    fall through to their rule-based fallback.
    """
    if not settings.claude_api_key:
        logger.warning("CLAUDE_API_KEY not set — skipping Claude call")
        return ""

    try:
        client = _get_client()
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.messages.create(
                model=settings.claude_model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            ),
        )
        return response.content[0].text
    except Exception as exc:
        logger.error("Claude API call failed: %s", exc)
        return ""


# ──────────────────────────────────────────────────────────────────────────
# 1. Agent Behavior Reasoning
# ──────────────────────────────────────────────────────────────────────────

async def generate_agent_behavior(
    agents_sample: list[dict],
    environment: dict,
    history: list[dict] | None = None,
) -> list[dict]:
    """
    Ask Claude to decide the immediate behavioral response for a sample of agents.

    Called every 50 simulation ticks on a sample of 10 agents to add
    AI-driven nuance on top of the physics engine.

    Parameters
    ----------
    agents_sample : list[dict]
        Each dict has keys: id, archetype, x, y, panic_level, state.
    environment : dict
        Simulation context: venue, capacity, incident type, elapsed time.
    history : list[dict] | None
        Recent tick history (optional, used for trend awareness).

    Returns
    -------
    list[dict]
        One dict per agent:
        {"agent_id": int, "action": str, "speed_modifier": float,
         "panic_level": float, "direction": str}
    """
    if not settings.claude_api_key:
        return _fallback_agent_behavior(agents_sample)

    history_str = ""
    if history:
        history_str = f"\nRecent history (last 3 snapshots):\n{json.dumps(history[-3:], indent=2)}"

    prompt = f"""You are simulating crowd behavior at a live event. Respond ONLY with valid JSON.

Event context:
{json.dumps(environment, indent=2)}
{history_str}

For each agent below, decide their immediate behavioral response given
their archetype, position, and the current incident.

Agents:
{json.dumps(agents_sample, indent=2)}

Return a JSON array — one object per agent:
[{{"agent_id": int, "action": str, "speed_modifier": float (0.5-2.0),
   "panic_level": float (0.0-1.0), "direction": str}}]

action must be one of: move_toward_exit, hold_position, follow_crowd,
assist_others, obstruct_flow, seek_information"""

    raw = await make_claude_call(prompt, max_tokens=1024)
    if not raw:
        return _fallback_agent_behavior(agents_sample)

    try:
        return _extract_json(raw)
    except Exception:
        return _fallback_agent_behavior(agents_sample)


def _fallback_agent_behavior(agents_sample: list[dict]) -> list[dict]:
    """Rule-based fallback when Claude is unavailable."""
    results = []
    for agent in agents_sample:
        panic = agent.get("panic_level", 0.2)
        archetype = agent.get("archetype", "casual")
        if archetype == "staff":
            action, direction = "assist_others", "incident"
        elif archetype == "non_compliant":
            action, direction = "obstruct_flow", "stage"
        elif panic > 0.5:
            action, direction = "move_toward_exit", "exit"
        else:
            action, direction = "hold_position", "none"
        results.append({
            "agent_id": agent.get("id", 0),
            "action": action,
            "speed_modifier": 1.5 if panic > 0.5 else 1.0,
            "panic_level": panic,
            "direction": direction,
        })
    return results


# ──────────────────────────────────────────────────────────────────────────
# 2. Signal Interpretation
# ──────────────────────────────────────────────────────────────────────────

async def interpret_ambiguous_signals(
    signal_data: dict,
    venue_context: dict | None = None,
) -> dict:
    """
    Use Claude for NLP over contradictory or ambiguous signal data.

    Called when composite risk score exceeds 0.60, or when two or more
    signals point in opposite directions (e.g., Twitter panic but low density).

    Parameters
    ----------
    signal_data : dict
        Current signal bundle: twitter, weather, crowd_density, ticket_velocity
        scores and raw values.
    venue_context : dict | None
        Venue details (name, capacity, event type) for grounding the analysis.

    Returns
    -------
    dict
        {"sentiment_label": str, "confidence": float, "primary_risk": str,
         "alert": str, "confidence_note": str}
        sentiment_label is one of: calm | rising | agitated | panicked
    """
    if not settings.claude_api_key:
        return _fallback_signal_interpretation(signal_data)

    ctx_str = f"\nVenue context:\n{json.dumps(venue_context, indent=2)}" if venue_context else ""

    prompt = f"""You are a crowd safety analyst reviewing live event signals. Respond ONLY with valid JSON.

Current signals:
{json.dumps(signal_data, indent=2)}
{ctx_str}

Identify:
1. The primary risk driver
2. Any contradictions between signals
3. A 2-sentence alert for event organizers (specific, actionable)
4. Overall crowd sentiment label

Output JSON:
{{"sentiment_label": "calm|rising|agitated|panicked",
  "confidence": float (0.0-1.0),
  "primary_risk": str,
  "alert": str,
  "confidence_note": str}}"""

    raw = await make_claude_call(prompt, max_tokens=512)
    if not raw:
        return _fallback_signal_interpretation(signal_data)

    try:
        return _extract_json(raw)
    except Exception:
        return _fallback_signal_interpretation(signal_data)


def _fallback_signal_interpretation(signal_data: dict) -> dict:
    composite = signal_data.get("composite_score", 0.5)
    label = "calm" if composite < 0.3 else "rising" if composite < 0.6 else "agitated" if composite < 0.8 else "panicked"
    return {
        "sentiment_label": label,
        "confidence": 0.6,
        "primary_risk": "composite",
        "alert": f"Risk score {composite:.2f} detected. Manual review recommended.",
        "confidence_note": "Rule-based fallback — Claude API not configured.",
    }


# ──────────────────────────────────────────────────────────────────────────
# 3. Scenario Generation
# ──────────────────────────────────────────────────────────────────────────

async def generate_scenarios(
    event_data: dict,
    current_state: dict | None = None,
) -> list[dict]:
    """
    Ask Claude to suggest stress-test what-if scenarios for an event.

    Called on-demand when the organizer clicks "Suggest Scenarios" in the dashboard.
    Results are cached per (event_id, event_type) to avoid repeat API calls.

    Parameters
    ----------
    event_data : dict
        Event configuration: venue_name, capacity, event_type, expected_attendance,
        artist_or_team, demographics, known_risks.
    current_state : dict | None
        Current live signals (optional — provides real-time grounding).

    Returns
    -------
    list[dict]
        Up to 3 scenario objects:
        [{"name": str, "description": str, "incident_type": str,
          "trigger_time": int, "severity": str, "parameters": dict}]
    """
    if not settings.claude_api_key:
        return _fallback_scenarios(event_data)

    state_str = f"\nCurrent live state:\n{json.dumps(current_state, indent=2)}" if current_state else ""

    prompt = f"""You are a crowd safety consultant preparing stress-test scenarios for a live event.
Respond ONLY with valid JSON.

Event details:
{json.dumps(event_data, indent=2)}
{state_str}

Generate 3 realistic but challenging what-if scenarios that would stress-test
this event's safety plan. Each should be specific to this event type and location.

Output JSON array:
[{{"name": str,
   "description": str,
   "incident_type": "crowd_surge|medical|fire|weather|evacuation|fight",
   "trigger_time": int (seconds into event, 0-7200),
   "severity": "low|medium|high",
   "parameters": {{}}}}]"""

    raw = await make_claude_call(prompt, max_tokens=1024)
    if not raw:
        return _fallback_scenarios(event_data)

    try:
        return _extract_json(raw)
    except Exception:
        return _fallback_scenarios(event_data)


def _fallback_scenarios(event_data: dict) -> list[dict]:
    event_type = event_data.get("event_type", "concert")
    return [
        {
            "name": "Stage Rush",
            "description": f"Fans surge toward stage after surprise announcement at {event_data.get('venue_name', 'venue')}.",
            "incident_type": "crowd_surge",
            "trigger_time": 1800,
            "severity": "high",
            "parameters": {"surge_multiplier": 2.0, "origin": "main_stage"},
        },
        {
            "name": "Medical Emergency Cluster",
            "description": "Multiple heat-related medical incidents near centre crowd.",
            "incident_type": "medical",
            "trigger_time": 900,
            "severity": "medium",
            "parameters": {"affected_radius_m": 30, "incident_count": 4},
        },
        {
            "name": "Controlled Evacuation",
            "description": "Orderly evacuation drill with low-urgency PA announcement.",
            "incident_type": "evacuation",
            "trigger_time": 3600,
            "severity": "low",
            "parameters": {"announcement_delay_s": 60, "staff_directed": True},
        },
    ]


# ──────────────────────────────────────────────────────────────────────────
# 4. Recommendations
# ──────────────────────────────────────────────────────────────────────────

async def generate_recommendations(
    predictions: dict,
    current_state: dict,
) -> list[dict]:
    """
    Ask Claude to produce prioritized, actionable recommendations for organizers.

    Called once after each simulation completes. Uses `max_tokens=1024` —
    recommendations are concise action items, not essays.

    Parameters
    ----------
    predictions : dict
        Simulation results: evacuation_time, bottlenecks, peak_density,
        injury_risk, agent_outcomes, crowd_sentiment_trajectory.
    current_state : dict
        Event config: venue_name, capacity, scenario, incident type.

    Returns
    -------
    list[dict]
        Up to 5 recommendations:
        [{"priority": int (1-5), "action": str, "location": str,
          "timing": str, "expected_impact": str}]
    """
    if not settings.claude_api_key:
        return _fallback_recommendations(predictions)

    prompt = f"""You are a crowd safety expert reviewing simulation results for a live event.
Respond ONLY with valid JSON.

Event context:
{json.dumps(current_state, indent=2)}

Simulation findings:
{json.dumps(predictions, indent=2)}

Provide 5 specific, actionable recommendations for the event organizer to reduce risk.
Prioritize by impact. Be specific: include locations, staffing numbers, and timings.

Output JSON array:
[{{"priority": int (1-5),
   "action": str,
   "location": str,
   "timing": str,
   "expected_impact": str}}]"""

    raw = await make_claude_call(prompt, max_tokens=1024)
    if not raw:
        return _fallback_recommendations(predictions)

    try:
        return _extract_json(raw)
    except Exception:
        return _fallback_recommendations(predictions)


def _fallback_recommendations(predictions: dict) -> list[dict]:
    evac = predictions.get("evacuation_time_seconds", 600)
    bottlenecks = predictions.get("bottlenecks", [])
    bn_loc = bottlenecks[0]["location"] if bottlenecks else "primary exit"
    return [
        {
            "priority": 1,
            "action": f"Deploy 4 additional staff to {bn_loc} to manage flow",
            "location": bn_loc,
            "timing": "Immediately",
            "expected_impact": f"Reduce evacuation time from {evac}s to ~{int(evac * 0.75)}s",
        },
        {
            "priority": 2,
            "action": "Open all emergency exit gates",
            "location": "All perimeter exits",
            "timing": "At incident detection (T+0s)",
            "expected_impact": "Increase exit capacity by ~40%",
        },
        {
            "priority": 3,
            "action": "Broadcast calm, directional PA announcement",
            "location": "Main PA system",
            "timing": "Within 30s of incident",
            "expected_impact": "Reduce non-compliant agent panic cascade by ~25%",
        },
        {
            "priority": 4,
            "action": "Station medical teams at identified high-density zones",
            "location": "High-density zones from simulation",
            "timing": "Pre-event setup",
            "expected_impact": "Cut response time to medical incidents by 3–5 minutes",
        },
        {
            "priority": 5,
            "action": "Review crowd profile — increase staff ratio if non-compliant > 5%",
            "location": "Staffing plan",
            "timing": "Pre-event",
            "expected_impact": "Reduce bottleneck formation probability by ~30%",
        },
    ]
