"""Tests for the Sparks entertainment module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_entertainment_scoring_returns_four_scores():
    """compute_sparks_scores() should return Safety, Revenue, Experience, Bottleneck."""
    from sparks.entertainment import compute_sparks_scores
    factors = {
        "composite_risk": 0.42,
        "fan_compliance_estimate": 0.65,
        "artist_hype_score": 0.75,
        "alcohol_policy_risk": 0.55,
        "historical_incident_rate": 0.18,
    }
    scores = compute_sparks_scores(factors)
    assert "Safety" in scores
    assert "Revenue" in scores
    assert "Experience" in scores
    assert "Bottleneck" in scores


def test_scores_in_valid_range():
    """All four scores must be 0–100."""
    from sparks.entertainment import compute_sparks_scores
    factors = {
        "composite_risk": 0.83,
        "fan_compliance_estimate": 0.65,
        "artist_hype_score": 0.85,
        "alcohol_policy_risk": 0.55,
        "historical_incident_rate": 0.18,
    }
    scores = compute_sparks_scores(factors)
    for key, val in scores.items():
        assert 0 <= val <= 100, f"{key}={val} out of range"


def test_high_risk_lowers_safety_score():
    """High composite risk should produce lower Safety score."""
    from sparks.entertainment import compute_sparks_scores

    safe_factors = {"composite_risk": 0.10, "fan_compliance_estimate": 0.90, "artist_hype_score": 0.5, "alcohol_policy_risk": 0.2, "historical_incident_rate": 0.05}
    risky_factors = {"composite_risk": 0.90, "fan_compliance_estimate": 0.30, "artist_hype_score": 0.9, "alcohol_policy_risk": 0.8, "historical_incident_rate": 0.25}

    safe_scores = compute_sparks_scores(safe_factors)
    risky_scores = compute_sparks_scores(risky_factors)

    assert safe_scores["Safety"] > risky_scores["Safety"]
    assert risky_scores["Bottleneck"] > safe_scores["Bottleneck"]


def test_evacuation_time_positive():
    """compute_evacuation_time() should return a positive integer."""
    from sparks.entertainment import compute_evacuation_time
    evac_time = compute_evacuation_time(
        venue_capacity=50000,
        actual_attendance=45000,
        exit_count=4,
        avg_exit_width_m=3.0,
        non_compliant_fraction=0.05,
    )
    assert evac_time > 0
    assert isinstance(evac_time, int)


def test_evacuation_time_scales_with_attendance():
    """More attendees should result in longer evacuation time."""
    from sparks.entertainment import compute_evacuation_time
    t_small = compute_evacuation_time(50000, 10000, 4)
    t_large = compute_evacuation_time(50000, 45000, 4)
    assert t_large > t_small


def test_bottleneck_zones_sorted_by_risk():
    """compute_bottleneck_zones() output should be sorted descending by risk_score."""
    from sparks.entertainment import compute_bottleneck_zones
    layout = {
        "exits": {
            "main_gate": {"width_m": 12, "nearby_capacity_fraction": 0.40},
            "side_exit": {"width_m": 3, "nearby_capacity_fraction": 0.25},
            "emergency": {"width_m": 2, "nearby_capacity_fraction": 0.10},
        }
    }
    zones = compute_bottleneck_zones(layout)
    if len(zones) > 1:
        for i in range(len(zones) - 1):
            assert zones[i]["risk_score"] >= zones[i + 1]["risk_score"]


def test_agent_archetypes_sum_to_one():
    """get_agent_archetypes_for_event() fractions should sum to ~1.0."""
    from sparks.entertainment import get_agent_archetypes_for_event
    for event_type in ("concert", "festival", "sports", "conference"):
        dist = get_agent_archetypes_for_event(event_type)
        total = sum(dist.values())
        assert abs(total - 1.0) < 0.01, f"{event_type}: fractions sum to {total}"


@pytest.mark.asyncio
async def test_entertainment_scorer_returns_profile():
    """EntertainmentScorer.get_risk_profile() should return expected keys."""
    from sparks.entertainment import EntertainmentScorer
    scorer = EntertainmentScorer("coachella_2023")
    profile = await scorer.get_risk_profile()
    assert "event_id" in profile
    assert "scores" in profile
    assert "factors" in profile
    assert profile["scores"]["Safety"] >= 0
