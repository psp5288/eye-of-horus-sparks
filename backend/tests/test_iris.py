"""Tests for the Iris monitoring module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_risk_scoring_returns_valid_range():
    """Risk score must be 0–1 for any input combination."""
    from iris.scorer import compute_risk_score
    from iris.models import SignalBundle, TwitterSignal, WeatherSignal, CrowdDensitySignal, TicketingSignal
    from datetime import datetime, timezone

    bundle = SignalBundle(
        event_id="test",
        timestamp=datetime.now(timezone.utc),
        twitter=TwitterSignal(sentiment_score=0.78, tweet_volume=5000),
        weather=WeatherSignal(temperature_f=87, humidity_pct=22, risk_score=0.18),
        crowd_density=CrowdDensitySignal(density_score=0.72, density_per_sqm=2.8),
        ticket_velocity=TicketingSignal(velocity_score=0.55),
    )
    result = compute_risk_score(bundle)
    assert 0.0 <= result.score <= 1.0
    assert 0.0 <= result.confidence <= 1.0
    assert result.level in ("LOW", "MODERATE", "HIGH", "CRITICAL")


def test_risk_scoring_critical_at_high_inputs():
    """High-risk inputs should produce CRITICAL or HIGH level."""
    from iris.scorer import compute_risk_score
    from iris.models import SignalBundle, TwitterSignal, WeatherSignal, CrowdDensitySignal, TicketingSignal
    from datetime import datetime, timezone

    bundle = SignalBundle(
        event_id="astroworld_test",
        timestamp=datetime.now(timezone.utc),
        twitter=TwitterSignal(sentiment_score=0.05),  # very negative
        weather=WeatherSignal(risk_score=0.9),
        crowd_density=CrowdDensitySignal(density_score=0.98),
        ticket_velocity=TicketingSignal(velocity_score=0.95),
    )
    result = compute_risk_score(bundle)
    assert result.level in ("HIGH", "CRITICAL"), f"Expected HIGH/CRITICAL, got {result.level}"
    assert result.score > 0.60


def test_risk_scoring_low_at_safe_inputs():
    """Safe inputs (indoor stadium, low density) should produce LOW risk."""
    from iris.scorer import compute_risk_score
    from iris.models import SignalBundle, TwitterSignal, WeatherSignal, CrowdDensitySignal, TicketingSignal
    from datetime import datetime, timezone

    bundle = SignalBundle(
        event_id="super_bowl_test",
        timestamp=datetime.now(timezone.utc),
        twitter=TwitterSignal(sentiment_score=0.85),
        weather=WeatherSignal(risk_score=0.05),
        crowd_density=CrowdDensitySignal(density_score=0.30),
        ticket_velocity=TicketingSignal(velocity_score=0.20),
    )
    result = compute_risk_score(bundle)
    assert result.level == "LOW", f"Expected LOW, got {result.level}"
    assert result.score < 0.30


def test_signal_bundle_defaults():
    """SignalBundle should have valid defaults for all fields."""
    from iris.models import SignalBundle
    from datetime import datetime, timezone

    bundle = SignalBundle(event_id="default_test", timestamp=datetime.now(timezone.utc))
    assert bundle.twitter.sentiment_score == 0.5
    assert bundle.weather.temperature_f == 72.0
    assert bundle.crowd_density.density_score == 0.5
    assert bundle.ticket_velocity.velocity_score == 0.4


def test_confidence_lower_when_signals_disagree():
    """Confidence should be < 0.9 when signals strongly contradict."""
    from iris.scorer import compute_risk_score
    from iris.models import SignalBundle, TwitterSignal, WeatherSignal, CrowdDensitySignal, TicketingSignal
    from datetime import datetime, timezone

    bundle = SignalBundle(
        event_id="contradiction_test",
        timestamp=datetime.now(timezone.utc),
        twitter=TwitterSignal(sentiment_score=0.05),  # very negative
        weather=WeatherSignal(risk_score=0.02),        # very safe
        crowd_density=CrowdDensitySignal(density_score=0.99),  # very dense
        ticket_velocity=TicketingSignal(velocity_score=0.01),   # very low
    )
    result = compute_risk_score(bundle)
    assert result.confidence < 0.9, f"Expected low confidence, got {result.confidence}"


@pytest.mark.asyncio
async def test_iris_monitor_returns_dict():
    """IrisMonitor.fetch_signals() should return a dict with expected keys."""
    from iris.monitor import IrisMonitor
    monitor = IrisMonitor()
    result = await monitor.fetch_signals("coachella_2023")
    assert "composite_risk" in result
    assert "risk_level" in result
    assert "signals" in result
    assert 0.0 <= result["composite_risk"] <= 1.0
