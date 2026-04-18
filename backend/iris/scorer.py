"""Risk scoring logic: combines signals into a composite risk score with confidence."""

from iris.models import SignalBundle, RiskLevel, score_to_risk_level


# Signal weights must sum to 1.0
SIGNAL_WEIGHTS = {
    "twitter_sentiment": 0.35,
    "crowd_density": 0.25,
    "weather": 0.25,
    "ticket_velocity": 0.15,
}


class RiskScorer:
    """Computes a composite risk score from a bundle of signals."""

    def compute(self, signals: SignalBundle) -> tuple[float, float]:
        """Return (composite_score, confidence) both in range [0, 1].

        Confidence is based on signal agreement — if all signals point the same
        direction, confidence is high. High variance = lower confidence.
        """
        scores = {
            "twitter_sentiment": signals.twitter_sentiment.score,
            "crowd_density": signals.crowd_density.score,
            "weather": signals.weather.score,
            "ticket_velocity": signals.ticket_velocity.score,
        }

        composite = sum(
            score * SIGNAL_WEIGHTS[key] for key, score in scores.items()
        )

        confidence = self._compute_confidence(list(scores.values()))
        return round(composite, 3), round(confidence, 3)

    def _compute_confidence(self, values: list[float]) -> float:
        """Higher agreement between signals → higher confidence."""
        if not values:
            return 0.5

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        # Max variance for [0,1] uniform is 0.0833. Map to 0.3–0.95 confidence.
        confidence = max(0.30, 0.95 - (variance / 0.083) * 0.65)
        return confidence

    def get_risk_level(self, score: float) -> RiskLevel:
        return score_to_risk_level(score)

    def get_recommendations(self, score: float, signals: SignalBundle) -> list[str]:
        """Rule-based recommendations based on score and signal values.

        Claude will replace / augment these for high-stakes situations.
        """
        recs = []

        if score >= 0.80:
            recs.append("CRITICAL: Consider pausing performances and activating emergency protocol.")

        if signals.crowd_density.score >= 0.75:
            recs.append("Open additional exit paths and activate crowd flow staff.")

        if signals.weather.score >= 0.40:
            recs.append(f"Weather alert: {', '.join(signals.weather.risk_factors)}. Brief attendees.")

        if signals.twitter_sentiment.score >= 0.65 and signals.twitter_sentiment.trend == "increasing":
            recs.append("Social media shows increasing negative sentiment. Monitor for crowd agitation.")

        if signals.ticket_velocity.resale_spike:
            recs.append("Ticket resale spike detected. Expect higher walkup attendance than projected.")

        if not recs:
            recs.append("No immediate action required. Continue routine monitoring.")

        return recs
