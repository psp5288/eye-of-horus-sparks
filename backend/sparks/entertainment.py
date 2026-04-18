"""
Entertainment-specific scoring for concerts, festivals, and sports events.

Produces four composite scores for the Sparks vertical:
  - Safety Score     (0–100) : Probability of a safe event, inverted risk
  - Revenue Score    (0–100) : Expected revenue health (attendance + merch + F&B)
  - Experience Score (0–100) : Fan experience quality
  - Bottleneck Score (0–100) : Severity of predicted crowd flow bottlenecks (lower = better)
"""

import logging
from typing import Optional

from sparks.venues import get_event, EventConfig

logger = logging.getLogger(__name__)


class EntertainmentScorer:
    """Computes entertainment-vertical scores for a given event."""

    def __init__(self, event_id: str):
        self.event_id = event_id
        self.event = get_event(event_id)

    async def get_risk_profile(self) -> dict:
        """
        Return the full entertainment risk profile.

        Returns
        -------
        dict
            entertainment_score, factors, comparable_events, risk_adjusted_capacity,
            and the four vertical scores (Safety, Revenue, Experience, Bottleneck).
        """
        if not self.event:
            return {"error": f"Event '{self.event_id}' not found"}

        factors = self._compute_factors(self.event)
        scores = compute_sparks_scores(factors, simulation_output=None)

        return {
            "event_id": self.event_id,
            "entertainment_score": round(factors["composite_risk"], 3),
            "scores": scores,
            "factors": factors,
            "comparable_events": self._find_comparable_events(self.event),
            "risk_adjusted_capacity": int(
                self.event.venue.capacity * (1.0 - factors["composite_risk"] * 0.15)
            ),
            "agent_archetypes": get_agent_archetypes_for_event(self.event.event_type),
        }

    def _compute_factors(self, event: EventConfig) -> dict:
        artist_hype     = self._score_artist_hype(event)
        fan_compliance  = self._score_fan_compliance(event)
        alcohol_risk    = self._score_alcohol_policy(event)
        historical_rate = self._historical_incident_rate(event)

        composite = (
            artist_hype         * 0.35
            + (1.0 - fan_compliance) * 0.25
            + alcohol_risk      * 0.25
            + historical_rate   * 0.15
        )

        return {
            "artist_hype_score":       round(artist_hype, 3),
            "fan_compliance_estimate": round(fan_compliance, 3),
            "alcohol_policy_risk":     round(alcohol_risk, 3),
            "historical_incident_rate": round(historical_rate, 3),
            "composite_risk":          round(composite, 3),
        }

    def _score_artist_hype(self, event: EventConfig) -> float:
        """Higher hype → higher crowd energy → elevated base risk."""
        base = {"festival": 0.75, "concert": 0.70, "sports": 0.60, "conference": 0.20}.get(
            event.event_type, 0.5
        )
        if event.venue.has_general_admission:
            base = min(1.0, base + 0.10)
        return base

    def _score_fan_compliance(self, event: EventConfig) -> float:
        """Estimate how compliant this crowd will be (higher = safer)."""
        return {"conference": 0.95, "sports": 0.75, "concert": 0.70, "festival": 0.65}.get(
            event.event_type, 0.70
        )

    def _score_alcohol_policy(self, event: EventConfig) -> float:
        """Outdoor festivals and amphitheaters carry higher alcohol risk."""
        return {"outdoor_festival": 0.55, "amphitheater": 0.50, "indoor_arena": 0.35, "stadium": 0.40}.get(
            event.venue.venue_type, 0.40
        )

    def _historical_incident_rate(self, event: EventConfig) -> float:
        """Historical incident rates per venue type (from industry data)."""
        return {"outdoor_festival": 0.18, "indoor_arena": 0.08, "stadium": 0.10, "amphitheater": 0.12}.get(
            event.venue.venue_type, 0.10
        )

    def _find_comparable_events(self, event: EventConfig) -> list[str]:
        return {
            "outdoor_festival": ["coachella_2023", "lollapalooza_2022"],
            "indoor_arena":     ["msg_concert_2023"],
            "stadium":          ["superbowl_lviii"],
        }.get(event.venue.venue_type, [])


# ──────────────────────────────────────────────────────────────────────────
# Core scoring functions
# ──────────────────────────────────────────────────────────────────────────

def compute_sparks_scores(
    factors: dict,
    simulation_output: Optional[dict] = None,
) -> dict:
    """
    Compute four composite scores for the Sparks vertical.

    Parameters
    ----------
    factors : dict
        Entertainment risk factors from EntertainmentScorer._compute_factors().
        Required keys: composite_risk, fan_compliance_estimate, artist_hype_score,
        alcohol_policy_risk, historical_incident_rate.
    simulation_output : dict | None
        Optional: Oracle simulation results (evacuation_time, bottlenecks,
        estimated_injury_risk, agent_outcomes). When provided, all four scores
        are grounded in simulation data, not estimates.

    Returns
    -------
    dict
        {"Safety": int, "Revenue": int, "Experience": int, "Bottleneck": int}
        All values 0–100. Higher is better EXCEPT Bottleneck (lower = fewer bottlenecks).

    Score formulas
    --------------
    Safety = (1 - composite_risk) × 70
           + fan_compliance × 20
           + (1 - historical_incident_rate) × 10
           [+ simulation adjustment if sim output provided]

    Revenue = fan_compliance × 40
            + (1 - alcohol_risk) × 20    ← alcohol risk hurts revenue through incidents
            + (1 - composite_risk) × 40

    Experience = (1 - artist_hype × crowd_friction) × 50
               + fan_compliance × 30
               + (1 - historical_incident_rate) × 20

    Bottleneck = composite_risk × 60
               + (1 - fan_compliance) × 25
               + historical_incident_rate × 15
               [+ simulation bottleneck severity if available]
    """
    composite    = factors.get("composite_risk", 0.5)
    compliance   = factors.get("fan_compliance_estimate", 0.7)
    hype         = factors.get("artist_hype_score", 0.6)
    alcohol      = factors.get("alcohol_policy_risk", 0.4)
    hist_rate    = factors.get("historical_incident_rate", 0.1)

    # ── Safety (higher = safer event) ──
    safety = (
        (1.0 - composite)  * 70.0
        + compliance       * 20.0
        + (1.0 - hist_rate) * 10.0
    )
    if simulation_output:
        injury_risk = simulation_output.get("estimated_injury_risk", 0.1)
        evac_time   = simulation_output.get("evacuation_time_seconds", 600)
        evac_penalty = max(0.0, (evac_time - 480) / 480) * 10.0  # 8 min target
        safety -= injury_risk * 15.0 + evac_penalty
    safety = max(0.0, min(100.0, safety))

    # ── Revenue (higher = better revenue outcome) ──
    revenue = (
        compliance         * 40.0
        + (1.0 - alcohol)  * 20.0
        + (1.0 - composite) * 40.0
    )
    if simulation_output:
        at_risk  = simulation_output.get("agent_outcomes", {}).get("at_risk", 0)
        n_agents = max(simulation_output.get("agent_outcomes", {}).get("safely_evacuated", 1000), 1)
        revenue -= (at_risk / n_agents) * 20.0
    revenue = max(0.0, min(100.0, revenue))

    # ── Experience (higher = better fan experience) ──
    # High hype + compliance = great show; high hype + low compliance = chaos
    crowd_friction = hype * (1.0 - compliance)
    experience = (
        (1.0 - crowd_friction) * 50.0
        + compliance           * 30.0
        + (1.0 - hist_rate)    * 20.0
    )
    if simulation_output:
        trajectory = simulation_output.get("crowd_sentiment_trajectory", [])
        if trajectory:
            final_sentiment = trajectory[-1]
            experience += (final_sentiment - 0.5) * 10.0
    experience = max(0.0, min(100.0, experience))

    # ── Bottleneck severity (lower = fewer/milder bottlenecks) ──
    bottleneck = (
        composite          * 60.0
        + (1.0 - compliance) * 25.0
        + hist_rate        * 15.0
    )
    if simulation_output:
        bns = simulation_output.get("bottlenecks", [])
        if bns:
            max_pressure = max(b.get("peak_pressure", 0) for b in bns)
            bottleneck += min(20.0, max_pressure * 2.0)
    bottleneck = max(0.0, min(100.0, bottleneck))

    return {
        "Safety":    int(round(safety)),
        "Revenue":   int(round(revenue)),
        "Experience": int(round(experience)),
        "Bottleneck": int(round(bottleneck)),
    }


def get_agent_archetypes_for_event(event_type: str) -> dict[str, float]:
    """
    Return the recommended agent archetype distribution for an event type.

    Parameters
    ----------
    event_type : str
        One of: "concert", "festival", "sports", "conference".

    Returns
    -------
    dict[str, float]
        Distribution summing to 1.0, suitable for passing to SwarmSimulation.
    """
    distributions = {
        "concert": {
            "casual": 0.35, "friends_group": 0.35,
            "influencer": 0.12, "staff": 0.12, "non_compliant": 0.06,
        },
        "festival": {
            "casual": 0.40, "friends_group": 0.28,
            "influencer": 0.15, "staff": 0.12, "non_compliant": 0.05,
        },
        "sports": {
            "casual": 0.45, "friends_group": 0.28,
            "influencer": 0.05, "staff": 0.18, "non_compliant": 0.04,
        },
        "conference": {
            "casual": 0.60, "friends_group": 0.15,
            "influencer": 0.10, "staff": 0.14, "non_compliant": 0.01,
        },
    }
    return distributions.get(
        event_type,
        {"casual": 0.40, "friends_group": 0.30, "influencer": 0.10, "staff": 0.15, "non_compliant": 0.05},
    )


def compute_evacuation_time(
    venue_capacity: int,
    actual_attendance: int,
    exit_count: int,
    avg_exit_width_m: float = 3.0,
    non_compliant_fraction: float = 0.05,
) -> int:
    """
    Estimate evacuation time in seconds using a simplified flow model.

    Formula: time = (attendance / (exit_count × throughput_per_exit))
             adjusted for non-compliance factor.

    Parameters
    ----------
    venue_capacity : int
    actual_attendance : int
    exit_count : int
        Number of functional exits.
    avg_exit_width_m : float
        Average exit width in metres (default 3.0m — one double-door).
    non_compliant_fraction : float
        Fraction of crowd that won't follow instructions (0.0–1.0).

    Returns
    -------
    int
        Estimated evacuation time in seconds.
    """
    # Standard flow: ~1.33 persons/metre/second (SFPE Handbook baseline)
    base_throughput_per_m = 1.33
    throughput_per_exit = base_throughput_per_m * avg_exit_width_m  # persons/second

    total_throughput = exit_count * throughput_per_exit
    if total_throughput <= 0:
        return 9999

    base_time = actual_attendance / total_throughput

    # Non-compliant agents slow flow by blocking exits; penalty is super-linear
    nc_penalty = 1.0 + (non_compliant_fraction * 2.5)

    # Density factor: high density slows movement
    density_factor = max(1.0, (actual_attendance / venue_capacity) * 1.3)

    return int(base_time * nc_penalty * density_factor)


def compute_bottleneck_zones(
    venue_layout: dict,
    crowd_density_map: dict | None = None,
) -> list[dict]:
    """
    Identify probable bottleneck zones for a venue layout.

    Parameters
    ----------
    venue_layout : dict
        Exit locations, corridors, choke points from Venue model.
    crowd_density_map : dict | None
        Optional real-time density grid (zone → density score).

    Returns
    -------
    list[dict]
        Sorted by risk (highest first):
        [{"zone": str, "risk_score": float, "reason": str}]
    """
    bottlenecks = []

    for exit_id, exit_info in venue_layout.get("exits", {}).items():
        width = exit_info.get("width_m", 3.0)
        nearby_capacity = exit_info.get("nearby_capacity_fraction", 0.25)

        risk = (nearby_capacity / max(width, 0.5)) * 10.0

        if crowd_density_map:
            zone_density = crowd_density_map.get(exit_id, 0.5)
            risk *= (1.0 + zone_density)

        bottlenecks.append({
            "zone": exit_id,
            "risk_score": round(min(risk, 10.0), 2),
            "reason": f"Width {width}m serves ~{nearby_capacity * 100:.0f}% of crowd",
        })

    return sorted(bottlenecks, key=lambda x: x["risk_score"], reverse=True)
