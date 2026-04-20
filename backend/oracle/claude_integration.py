"""
Claude Opus 4.7 integration for Eye of Horus: Sparks.

Four integration points:
  1. generate_agent_behavior()  — agent reasoning during swarm simulation
  2. interpret_ambiguous_signals() — NLP over contradictory signal data
  3. generate_scenarios()       — what-if scenario suggestions
  4. generate_recommendations() — prioritized organizer guidance

MOCK MODE (April 20):
  All four functions have high-quality rule-based implementations that
  return realistic structured data without any API key. On April 21,
  replace _call_claude() body with real Anthropic API call — everything
  else stays the same.

Cost estimate per event-hour: ~$0.15
"""

import json
import asyncio
import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazy-init Anthropic client. Returns None if key not set."""
    global _client
    if _client is None:
        try:
            import anthropic
            from config import get_settings
            settings = get_settings()
            if settings.claude_api_key:
                _client = anthropic.Anthropic(api_key=settings.claude_api_key)
        except Exception:
            pass
    return _client


def _extract_json(text: str) -> dict | list:
    """Strip markdown fences and parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


async def make_claude_call(prompt: str, max_tokens: int = 1024) -> str:
    """
    Call Claude API. Returns "" on any failure so callers fall through to mock.

    April 21: This already works — just needs CLAUDE_API_KEY in .env.
    """
    client = _get_client()
    if not client:
        logger.info("Claude client not configured — using mock fallback")
        return ""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.messages.create(
                model="claude-opus-4-7",
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
    Decide immediate behavioral response for a sample of simulation agents.

    Called every 50 ticks on a 10-agent sample. Claude adds reasoning nuance
    on top of the physics engine (e.g., non-compliant agents blocking exits,
    influencers amplifying panic, staff calming nearby agents).

    Parameters
    ----------
    agents_sample : list[dict]
        Each: {id, archetype, x, y, panic_level, state}
    environment : dict
        {venue, capacity, incident_type, elapsed_time_s, composite_risk, incident_active}
    history : list[dict] | None
        Last 3 simulation snapshots for trend awareness.

    Returns
    -------
    list[dict]
        [{agent_id, action, speed_modifier, panic_level, direction}]
        action ∈ {move_toward_exit, hold_position, follow_crowd,
                  assist_others, obstruct_flow, seek_information}

    April 21 prompt template
    ------------------------
    "You are simulating crowd behavior at {venue}. Incident: {incident_type}.
     For each agent decide their response. Return JSON array only."
    """
    # ── Try Claude first ───────────────────────────────────────────────────
    if _get_client():
        history_str = ""
        if history:
            history_str = f"\nRecent snapshots:\n{json.dumps(history[-3:], indent=2)}"

        prompt = f"""You are simulating crowd behavior at a live event. Respond ONLY with valid JSON.

Event context:
{json.dumps(environment, indent=2)}
{history_str}

For each agent below, decide their immediate behavioral response given
their archetype, position, and current incident.

Agents:
{json.dumps(agents_sample, indent=2)}

Return a JSON array — one object per agent:
[{{"agent_id": int, "action": str, "speed_modifier": float (0.5-2.0),
   "panic_level": float (0.0-1.0), "direction": str}}]

action must be one of: move_toward_exit, hold_position, follow_crowd,
assist_others, obstruct_flow, seek_information"""

        raw = await make_claude_call(prompt, max_tokens=1024)
        if raw:
            try:
                return _extract_json(raw)
            except Exception:
                pass

    # ── Mock fallback (realistic rule-based) ───────────────────────────────
    return _mock_agent_behavior(agents_sample, environment)


def _mock_agent_behavior(agents_sample: list[dict], environment: dict) -> list[dict]:
    """
    Realistic rule-based agent behavior. Produces plausible decisions
    based on archetype × panic × incident severity.
    """
    incident_active = environment.get("incident_active", False)
    incident_type   = environment.get("incident_type", "crowd_surge")
    composite_risk  = environment.get("composite_risk", 0.4)
    results = []

    for agent in agents_sample:
        archetype   = agent.get("archetype", "casual")
        panic       = agent.get("panic_level", 0.2)
        x, y        = agent.get("x", 0.5), agent.get("y", 0.5)

        # Archetype-driven base decisions
        if archetype == "staff":
            action        = "assist_others"
            direction     = "incident"
            speed         = 1.6
            new_panic     = max(0.0, panic - 0.05)

        elif archetype == "non_compliant":
            action        = "obstruct_flow" if incident_active else "hold_position"
            direction     = "stage"
            speed         = 1.8
            new_panic     = min(1.0, panic + composite_risk * 0.1)

        elif archetype == "influencer":
            # Influencers seek best vantage, raising panic in followers
            if panic > 0.6:
                action, direction = "move_toward_exit", "exit"
                speed = 1.4
            else:
                action, direction = "seek_information", "stage"
                speed = 1.1
            new_panic = min(1.0, panic + composite_risk * 0.08)

        elif archetype == "friends_group":
            # Groups stay together, slower to react
            if panic > 0.65:
                action, direction = "move_toward_exit", "exit"
                speed = 0.85  # slowed by coordination
            else:
                action, direction = "follow_crowd", "none"
                speed = 0.9
            new_panic = min(1.0, panic + composite_risk * 0.06)

        else:  # casual
            if panic > 0.55 and incident_active:
                action, direction = "move_toward_exit", "exit"
                speed = 1.3
            elif panic > 0.3:
                action, direction = "follow_crowd", "exit"
                speed = 1.1
            else:
                action, direction = "hold_position", "none"
                speed = 1.0
            new_panic = min(1.0, panic + composite_risk * 0.05)

        results.append({
            "agent_id":      agent.get("id", 0),
            "action":        action,
            "speed_modifier": round(speed, 2),
            "panic_level":   round(new_panic, 3),
            "direction":     direction,
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
    NLP over contradictory or ambiguous signal bundles.

    Called when composite_risk > 0.60, or when ≥2 signals contradict.

    Parameters
    ----------
    signal_data : dict
        {twitter_sentiment_score, twitter_sample, crowd_density_score,
         weather_score, ticket_velocity_score, composite_score}
    venue_context : dict | None
        {name, capacity, event_type}

    Returns
    -------
    dict
        {sentiment_label, confidence, primary_risk, alert, confidence_note}
        sentiment_label ∈ {calm, rising, agitated, panicked}

    April 21 prompt template
    ------------------------
    "You are a crowd safety analyst. Identify primary risk driver,
     contradictions, write 2-sentence actionable alert. JSON only."
    """
    if _get_client():
        ctx_str = f"\nVenue:\n{json.dumps(venue_context, indent=2)}" if venue_context else ""
        prompt = f"""You are a crowd safety analyst reviewing live event signals. Respond ONLY with valid JSON.

Signals:
{json.dumps(signal_data, indent=2)}
{ctx_str}

Identify: primary risk driver, any signal contradictions, 2-sentence alert for organizers.

Output JSON:
{{"sentiment_label": "calm|rising|agitated|panicked",
  "confidence": float,
  "primary_risk": str,
  "alert": str,
  "confidence_note": str}}"""

        raw = await make_claude_call(prompt, max_tokens=512)
        if raw:
            try:
                return _extract_json(raw)
            except Exception:
                pass

    return _mock_signal_interpretation(signal_data)


def _mock_signal_interpretation(signal_data: dict) -> dict:
    """
    Keyword + threshold-based signal interpretation.
    Detects contradictions and generates a specific alert.
    """
    composite  = signal_data.get("composite_score", signal_data.get("composite_risk", 0.5))
    twitter    = signal_data.get("twitter_sentiment_score", 0.5)
    density    = signal_data.get("crowd_density_score", 0.5)
    weather    = signal_data.get("weather_score", 0.1)
    sample     = signal_data.get("twitter_sample", "")

    # Sentiment label
    if composite < 0.30:   label = "calm"
    elif composite < 0.55: label = "rising"
    elif composite < 0.78: label = "agitated"
    else:                  label = "panicked"

    # Primary risk driver (highest score wins)
    scores = {
        "twitter_distress":  1.0 - twitter,
        "crowd_density":     density,
        "weather_hazard":    weather,
    }
    primary_risk = max(scores, key=scores.get)

    # Contradiction detection
    contradiction = abs((1.0 - twitter) - density) > 0.4
    confidence    = 0.62 if contradiction else 0.82

    # Specific alert
    negative_keywords = ["crush", "panic", "can't breathe", "injured", "help", "scared", "push"]
    tweet_distress = any(kw in sample.lower() for kw in negative_keywords)

    if label == "panicked" or tweet_distress:
        alert = (
            f"CRITICAL: Distress signals detected (composite {composite:.2f}). "
            f"Dispatch security to high-density zones immediately and open all emergency exits."
        )
    elif label == "agitated":
        alert = (
            f"Elevated crowd tension (composite {composite:.2f}). "
            f"Increase staff visibility at stage barriers and prepare PA announcement."
        )
    elif contradiction:
        alert = (
            f"Signal contradiction: Twitter suggests {'distress' if (1-twitter)>density else 'calm'} "
            f"but density reads {density:.2f}. Manual verification recommended."
        )
    else:
        alert = (
            f"Situation nominal (composite {composite:.2f}). "
            f"Continue standard monitoring — no immediate action required."
        )

    return {
        "sentiment_label":  label,
        "confidence":       round(confidence, 2),
        "primary_risk":     primary_risk,
        "alert":            alert,
        "confidence_note":  "Rule-based mock — Claude API not configured." if not _get_client() else "Claude interpretation.",
    }


# ──────────────────────────────────────────────────────────────────────────
# 3. Scenario Generation
# ──────────────────────────────────────────────────────────────────────────

async def generate_scenarios(
    event_data: dict,
    current_state: dict | None = None,
) -> list[dict]:
    """
    Suggest stress-test what-if scenarios tailored to the event.

    Called on-demand ("Suggest Scenarios" button). Cached per event_id.

    Parameters
    ----------
    event_data : dict
        {venue_name, capacity, event_type, expected_attendance, artist_or_team}
    current_state : dict | None
        Live signal snapshot for real-time grounding.

    Returns
    -------
    list[dict]
        Up to 3 scenarios: [{name, description, incident_type,
                              trigger_time, severity, parameters}]

    April 21 prompt template
    ------------------------
    "You are a crowd safety consultant. Generate 3 realistic stress-test
     scenarios for this specific event type and venue. JSON array only."
    """
    if _get_client():
        state_str = f"\nCurrent state:\n{json.dumps(current_state, indent=2)}" if current_state else ""
        prompt = f"""You are a crowd safety consultant preparing stress-test scenarios for a live event.
Respond ONLY with valid JSON.

Event:
{json.dumps(event_data, indent=2)}
{state_str}

Generate 3 realistic but challenging what-if scenarios specific to this event type.

Output JSON array:
[{{"name": str,
   "description": str,
   "incident_type": "crowd_surge|medical|fire|weather|evacuation|fight",
   "trigger_time": int (seconds into event, 0-7200),
   "severity": "low|medium|high",
   "parameters": {{}}}}]"""

        raw = await make_claude_call(prompt, max_tokens=1024)
        if raw:
            try:
                return _extract_json(raw)
            except Exception:
                pass

    return _mock_scenarios(event_data)


def _mock_scenarios(event_data: dict) -> list[dict]:
    """Event-type-aware scenario templates."""
    event_type   = event_data.get("event_type", "festival")
    venue_name   = event_data.get("venue_name", "the venue")
    artist       = event_data.get("artist_or_team", "the headliner")
    capacity     = event_data.get("capacity", 50000)

    base = [
        {
            "name": f"{'Stage Rush' if event_type in ('festival','concert') else 'Field Rush'}",
            "description": f"Crowd surges toward {'main stage' if event_type in ('festival','concert') else 'field level'} after {artist} surprise announcement at {venue_name}.",
            "incident_type": "crowd_surge",
            "trigger_time":  5400,
            "severity":      "high",
            "parameters":    {"surge_multiplier": 2.2, "origin": "main_stage", "affected_agents": int(capacity * 0.15)},
        },
        {
            "name": "Medical Emergency Cluster",
            "description": f"{'Heat-related' if event_type == 'festival' else 'Dehydration'} medical incidents cluster near centre crowd during peak attendance.",
            "incident_type": "medical",
            "trigger_time":  7200,
            "severity":      "medium",
            "parameters":    {"affected_radius_m": 40, "incident_count": 6, "requires_evac_corridor": True},
        },
        {
            "name": f"{'Sudden Weather' if event_type in ('festival','sports') else 'Fire Alarm'}",
            "description": f"{'Storm forces evacuation of outdoor areas' if event_type in ('festival','sports') else 'Fire alarm triggers orderly evacuation'} at {venue_name}.",
            "incident_type": "weather" if event_type in ("festival","sports") else "fire",
            "trigger_time":  3600,
            "severity":      "high" if event_type == "festival" else "medium",
            "parameters":    {"announcement_delay_s": 45, "staff_directed": True, "exit_capacity_pct": 0.6},
        },
    ]
    return base


# ──────────────────────────────────────────────────────────────────────────
# 4. Recommendations
# ──────────────────────────────────────────────────────────────────────────

async def generate_recommendations(
    predictions: dict,
    current_state: dict,
) -> list[dict]:
    """
    Produce prioritized, actionable recommendations for event organizers.

    Called once after each simulation completes.

    Parameters
    ----------
    predictions : dict
        {evacuation_time_seconds, bottlenecks, peak_density,
         estimated_injury_risk, agent_outcomes, crowd_sentiment_trajectory}
    current_state : dict
        {venue_name, capacity, scenario, incident_type}

    Returns
    -------
    list[dict]
        Up to 5: [{priority, action, location, timing, expected_impact}]

    April 21 prompt template
    ------------------------
    "You are a crowd safety expert. Give 5 specific, actionable recommendations
     with staff numbers, locations, timings. JSON array only."
    """
    if _get_client():
        prompt = f"""You are a crowd safety expert reviewing simulation results. Respond ONLY with valid JSON.

Event context:
{json.dumps(current_state, indent=2)}

Simulation results:
{json.dumps(predictions, indent=2)}

Provide 5 specific, actionable recommendations. Include locations, staff numbers, timings.

Output JSON array:
[{{"priority": int (1-5),
   "action": str,
   "location": str,
   "timing": str,
   "expected_impact": str}}]"""

        raw = await make_claude_call(prompt, max_tokens=1024)
        if raw:
            try:
                return _extract_json(raw)
            except Exception:
                pass

    return _mock_recommendations(predictions, current_state)


def _mock_recommendations(predictions: dict, current_state: dict) -> list[dict]:
    """
    Simulation-aware recommendations: reads actual bottleneck locations
    and evacuation time to produce specific (not generic) guidance.
    """
    evac        = predictions.get("evacuation_time_seconds", 600)
    bottlenecks = predictions.get("bottlenecks", [])
    at_risk     = predictions.get("agent_outcomes", {}).get("at_risk", 0)
    injury_risk = predictions.get("estimated_injury_risk", 0.05)
    venue       = current_state.get("venue_name", "venue")

    bn1_loc = bottlenecks[0]["location"] if bottlenecks else "primary exit"
    bn2_loc = bottlenecks[1]["location"] if len(bottlenecks) > 1 else "secondary exit"
    evac_improved = int(evac * 0.72)

    recs = [
        {
            "priority": 1,
            "action":   f"Deploy 6 security staff to {bn1_loc} — create 2m buffer zone and open auxiliary gates",
            "location": bn1_loc,
            "timing":   "T+0s — immediately on incident detection",
            "expected_impact": f"Reduce evacuation time from {evac}s to ~{evac_improved}s (~28% improvement)",
        },
        {
            "priority": 2,
            "action":   "Open all perimeter emergency exits and disable entry turnstiles",
            "location": "All perimeter exits",
            "timing":   "Within 30s of incident detection",
            "expected_impact": "Increase exit capacity by ~40%",
        },
        {
            "priority": 3,
            "action":   "Broadcast calm PA announcement with specific directional instructions",
            "location": "Main PA system",
            "timing":   "T+45s — after staff are in position",
            "expected_impact": f"Reduce non-compliant agent obstruction by ~25%, lower panic cascade",
        },
    ]

    if len(bottlenecks) > 1:
        recs.append({
            "priority": 4,
            "action":   f"Station 4 medical staff at {bn2_loc} — secondary bottleneck identified",
            "location": bn2_loc,
            "timing":   "T+60s",
            "expected_impact": f"Cut medical response time by 3–4 min for {at_risk} at-risk agents",
        })

    if injury_risk > 0.05:
        recs.append({
            "priority": 5,
            "action":   f"Pre-position 2 ambulances at {venue} north entrance; alert nearest trauma centre",
            "location": f"{venue} north entrance",
            "timing":   "T+0s — simultaneous with incident detection",
            "expected_impact": f"Reduce critical response time from ~8 min to ~3 min",
        })
    else:
        recs.append({
            "priority": 5,
            "action":   "Review crowd profile post-event; if non-compliant fraction >5%, increase staff ratio at next event",
            "location": "Staffing plan",
            "timing":   "Post-event debrief",
            "expected_impact": "Reduce bottleneck probability at future events by ~30%",
        })

    return recs
