"""Tests for the Iris monitoring module."""

import pytest
from iris.models import SignalBundle, TwitterSignalData, WeatherSignalData, CrowdDensityData, TicketVelocityData, RiskLevel, score_to_risk_level
from iris.scorer import RiskScorer


def make_signals(twitter=0.5, weather=0.1, density=0.6, velocity=0.3) -> SignalBundle:
    return SignalBundle(
        twitter_sentiment=TwitterSignalData(score=twitter),
        weather=WeatherSignalData(score=weather),
        crowd_density=CrowdDensityData(score=density),
        ticket_velocity=TicketVelocityData(score=velocity),
    )


class TestRiskScorer:
    def test_low_risk(self):
        scorer = RiskScorer()
        signals = make_signals(0.1, 0.05, 0.1, 0.1)
        score, confidence = scorer.compute(signals)
        assert score < 0.30
        assert scorer.get_risk_level(score) == RiskLevel.LOW

    def test_moderate_risk(self):
        scorer = RiskScorer()
        signals = make_signals(0.4, 0.2, 0.5, 0.3)
        score, confidence = scorer.compute(signals)
        assert 0.30 <= score < 0.60

    def test_high_risk(self):
        scorer = RiskScorer()
        signals = make_signals(0.75, 0.4, 0.8, 0.6)
        score, confidence = scorer.compute(signals)
        assert score >= 0.60

    def test_critical_risk(self):
        scorer = RiskScorer()
        signals = make_signals(0.95, 0.9, 0.95, 0.9)
        score, confidence = scorer.compute(signals)
        assert scorer.get_risk_level(score) == RiskLevel.CRITICAL

    def test_confidence_high_when_signals_agree(self):
        scorer = RiskScorer()
        signals = make_signals(0.8, 0.8, 0.8, 0.8)
        _, confidence = scorer.compute(signals)
        assert confidence >= 0.80

    def test_confidence_low_when_signals_disagree(self):
        scorer = RiskScorer()
        signals = make_signals(0.9, 0.05, 0.9, 0.05)
        _, confidence = scorer.compute(signals)
        assert confidence < 0.70

    def test_weighted_score(self):
        scorer = RiskScorer()
        # Only twitter high (weight 0.35), rest 0
        signals = make_signals(1.0, 0.0, 0.0, 0.0)
        score, _ = scorer.compute(signals)
        assert abs(score - 0.35) < 0.01

    def test_recommendations_not_empty(self):
        scorer = RiskScorer()
        signals = make_signals(0.8, 0.5, 0.85, 0.6)
        recs = scorer.get_recommendations(0.75, signals)
        assert len(recs) > 0


class TestRiskLevel:
    @pytest.mark.parametrize("score,expected", [
        (0.10, RiskLevel.LOW),
        (0.29, RiskLevel.LOW),
        (0.30, RiskLevel.MODERATE),
        (0.59, RiskLevel.MODERATE),
        (0.60, RiskLevel.HIGH),
        (0.79, RiskLevel.HIGH),
        (0.80, RiskLevel.CRITICAL),
        (1.00, RiskLevel.CRITICAL),
    ])
    def test_thresholds(self, score, expected):
        assert score_to_risk_level(score) == expected
