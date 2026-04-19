"""Signal ingestion stubs for Twitter, Weather, and Ticketing APIs."""

import asyncio
import logging
import random
from typing import Optional

from iris.models import TwitterSignal, WeatherSignal, CrowdDensitySignal, TicketingSignal

logger = logging.getLogger(__name__)

# Mock data keyed by event_id for demo/dev mode
_MOCK_SIGNALS = {
    "astroworld_2024": {
        "twitter": TwitterSignal(sentiment_score=0.78, sample_text="crowd pushing near south stage", tweet_volume=8400, raw_score=0.78),
        "weather": WeatherSignal(temperature_f=68, humidity_pct=55, conditions="Clear", wind_mph=8, risk_score=0.05),
        "density": CrowdDensitySignal(density_score=0.87, density_per_sqm=5.8, hotspots=["main_stage", "south_stage"]),
        "ticketing": TicketingSignal(velocity_score=0.85, resale_spike=True, resale_premium_pct=45),
    },
    "coachella_2023": {
        "twitter": TwitterSignal(sentiment_score=0.35, sample_text="long lines at north stage but vibe is incredible", tweet_volume=12400, raw_score=0.35),
        "weather": WeatherSignal(temperature_f=87, humidity_pct=22, conditions="Partly cloudy", wind_mph=12, risk_score=0.18),
        "density": CrowdDensitySignal(density_score=0.72, density_per_sqm=2.8, hotspots=["sahara_stage", "main_stage_pit"]),
        "ticketing": TicketingSignal(velocity_score=0.55, resale_spike=False, resale_premium_pct=15),
    },
    "super_bowl_58": {
        "twitter": TwitterSignal(sentiment_score=0.20, sample_text="incredible atmosphere, staff everywhere, super organized", tweet_volume=24000, raw_score=0.20),
        "weather": WeatherSignal(temperature_f=72, humidity_pct=30, conditions="Indoor, climate controlled", wind_mph=0, risk_score=0.08),
        "density": CrowdDensitySignal(density_score=0.55, density_per_sqm=1.8, hotspots=[]),
        "ticketing": TicketingSignal(velocity_score=0.40, resale_spike=False, resale_premium_pct=80),
    },
}


async def fetch_twitter_signal(event_id: str) -> TwitterSignal:
    """
    Fetch Twitter sentiment signal for an event.

    Uses Tweepy + VADER for real-time scoring, or mock data in dev mode.

    Parameters
    ----------
    event_id : str
        Event identifier.

    Returns
    -------
    TwitterSignal
        Sentiment score (0=negative, 1=positive), sample tweet, volume.
    """
    mock = _MOCK_SIGNALS.get(event_id, {}).get("twitter")
    if mock:
        return mock

    # TODO (April 21): implement Tweepy v2 + VADER live scoring
    # from tweepy import Client
    # from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    return TwitterSignal(sentiment_score=0.5, sample_text="No data", tweet_volume=0)


async def fetch_weather_signal(event_id: str) -> WeatherSignal:
    """
    Fetch weather signal from OpenWeatherMap for the event venue.

    Parameters
    ----------
    event_id : str
        Event identifier (used to look up venue lat/lon).

    Returns
    -------
    WeatherSignal
        Temperature, humidity, conditions, risk score.
    """
    mock = _MOCK_SIGNALS.get(event_id, {}).get("weather")
    if mock:
        return mock

    # TODO (April 21): implement OpenWeatherMap API call
    # import requests
    # resp = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}")
    return WeatherSignal()


async def fetch_crowd_density_signal(event_id: str) -> CrowdDensitySignal:
    """
    Estimate crowd density from available data sources.

    In production: ingests venue sensor data, social check-ins, or camera feeds.
    In demo mode: returns mock data keyed by event_id.

    Parameters
    ----------
    event_id : str
        Event identifier.

    Returns
    -------
    CrowdDensitySignal
        Density score, density per sqm, hotspot zone list.
    """
    mock = _MOCK_SIGNALS.get(event_id, {}).get("density")
    if mock:
        return mock

    return CrowdDensitySignal()


async def fetch_ticketing_signal(event_id: str) -> TicketingSignal:
    """
    Fetch ticket velocity and resale spike data.

    Parameters
    ----------
    event_id : str
        Event identifier.

    Returns
    -------
    TicketingSignal
        Velocity score, resale spike flag, resale premium %.
    """
    mock = _MOCK_SIGNALS.get(event_id, {}).get("ticketing")
    if mock:
        return mock

    # TODO (April 21): implement Ticketmaster API + resale market monitoring
    return TicketingSignal()


def parse_twitter_sentiment(text: str) -> float:
    """
    Score text sentiment with VADER (no API cost, runs locally).

    Parameters
    ----------
    text : str
        Raw tweet text.

    Returns
    -------
    float
        Compound sentiment score 0–1 (0=very negative, 1=very positive).
    """
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        compound = analyzer.polarity_scores(text)["compound"]
        return (compound + 1) / 2  # map -1..1 to 0..1
    except ImportError:
        return 0.5


def parse_weather_risk(temp_f: float, humidity: float, conditions: str) -> float:
    """
    Convert weather conditions into a risk score.

    High temperature + high humidity = higher medical incident probability.

    Parameters
    ----------
    temp_f : float
    humidity : float
    conditions : str

    Returns
    -------
    float
        Weather risk score 0–1.
    """
    heat_score = max(0.0, (temp_f - 75) / 40)       # 75°F = 0 risk, 115°F = 1.0
    humidity_score = max(0.0, (humidity - 40) / 60)  # 40% = 0 risk, 100% = 1.0

    condition_penalty = 0.0
    if any(w in conditions.lower() for w in ["rain", "storm", "thunder", "lightning"]):
        condition_penalty = 0.3
    elif "heat" in conditions.lower():
        condition_penalty = 0.2

    return min(1.0, heat_score * 0.5 + humidity_score * 0.3 + condition_penalty)
