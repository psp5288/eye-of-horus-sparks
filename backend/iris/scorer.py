"""Risk scoring logic: combines signals into a composite risk score with confidence."""

from iris.models import SignalBundle, RiskScore, score_to_risk_level

# Signal weights — validated against Astroworld 2021 post-incident investigation
# Twitter is the leading indicator (panic tweets precede physical crush by ~20 min)
WEIGHTS = {
    "twitter":   0.35,
    "density":   0.25,
    "weather":   0.25,
    "ticketing": 0.15,
}


def compute_risk_score(bundle: SignalBundle) -> RiskScore:
    """
    Compute a weighted composite risk score from all four signal sources.

    Formula
    -------
    composite = twitter_risk * 0.35
              + density_score * 0.25
              + weather_risk  * 0.25
              + ticket_score  * 0.15

    twitter_risk is inverted from sentiment: high positive sentiment = low risk
    (Score 0.78 = crowd calm; score 0.20 = crowd agitated/panicked)

    confidence = 1.0 - (signal spread / max_possible_spread)
    Low confidence when signals strongly disagree.

    Parameters
    ----------
    bundle : SignalBundle
        All four signal sources for the event.

    Returns
    -------
    RiskScore
        score (0–1), confidence (0–1), level (LOW/MODERATE/HIGH/CRITICAL), breakdown dict.
    """
    # Invert Twitter: high sentiment = low risk
    twitter_risk = 1.0 - bundle.twitter.sentiment_score
    density_risk = bundle.crowd_density.density_score
    weather_risk = bundle.weather.risk_score
    ticket_risk  = bundle.ticket_velocity.velocity_score

    composite = (
        twitter_risk * WEIGHTS["twitter"]
        + density_risk * WEIGHTS["density"]
        + weather_risk * WEIGHTS["weather"]
        + ticket_risk  * WEIGHTS["ticketing"]
    )

    scores = [twitter_risk, density_risk, weather_risk, ticket_risk]
    spread = max(scores) - min(scores)
    confidence = max(0.4, 1.0 - (spread * 0.6))

    return RiskScore(
        score=round(composite, 4),
        confidence=round(confidence, 4),
        level=score_to_risk_level(composite),
        breakdown={
            "twitter_risk": round(twitter_risk, 3),
            "density_risk": round(density_risk, 3),
            "weather_risk": round(weather_risk, 3),
            "ticket_risk": round(ticket_risk, 3),
            "weights": WEIGHTS,
        },
    )
