"""Signal ingestion stubs for Twitter, Weather, and Ticketing APIs."""

import asyncio
import random
from datetime import datetime
from typing import Optional

import httpx

from config import get_settings
from iris.models import (
    TwitterSignalData,
    WeatherSignalData,
    CrowdDensityData,
    TicketVelocityData,
)

settings = get_settings()


class TwitterSignalFetcher:
    """Fetches recent tweets for an event and computes sentiment score."""

    BASE_URL = "https://api.twitter.com/2/tweets/search/recent"

    def __init__(self, event_id: str, query_terms: Optional[list[str]] = None):
        self.event_id = event_id
        self.query_terms = query_terms or [event_id, "concert", "crowd"]

    async def fetch(self) -> TwitterSignalData:
        """Fetch tweets and return sentiment score.

        Falls back to simulated data when API key is not configured.
        """
        if not settings.twitter_bearer_token:
            return self._simulate()

        query = " OR ".join(self.query_terms) + " lang:en -is:retweet"
        params = {"query": query, "max_results": 100, "tweet.fields": "text,created_at"}
        headers = {"Authorization": f"Bearer {settings.twitter_bearer_token}"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.BASE_URL, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            return self._parse_response(data)
        except Exception:
            return self._simulate()

    def _parse_response(self, data: dict) -> TwitterSignalData:
        """Parse Twitter API response and compute VADER sentiment."""
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        tweets = data.get("data", [])
        if not tweets:
            return TwitterSignalData(score=0.5, tweet_count=0)

        analyzer = SentimentIntensityAnalyzer()
        scores = []
        for tweet in tweets:
            text = tweet.get("text", "")
            vs = analyzer.polarity_scores(text)
            # Invert compound: high negative sentiment = high risk score
            risk = (1.0 - vs["compound"]) / 2.0
            scores.append(risk)

        avg_score = sum(scores) / len(scores)
        sample = tweets[0].get("text", "") if tweets else ""
        trend = "increasing" if avg_score > 0.55 else "stable"

        return TwitterSignalData(
            score=round(avg_score, 3),
            tweet_count=len(tweets),
            sample_text=sample[:200],
            trend=trend,
        )

    def _simulate(self) -> TwitterSignalData:
        """Return plausible simulated data when API is unavailable."""
        score = round(random.uniform(0.2, 0.7), 3)
        return TwitterSignalData(
            score=score,
            tweet_count=random.randint(50, 800),
            sample_text="[simulated] crowd is getting really packed near the stage",
            trend="increasing" if score > 0.5 else "stable",
        )


class WeatherSignalFetcher:
    """Fetches current weather for a venue and computes weather risk score."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, lat: float = 34.0, lon: float = -118.0):
        self.lat = lat
        self.lon = lon

    async def fetch(self) -> WeatherSignalData:
        """Fetch weather data. Falls back to simulation when API key missing."""
        if not settings.openweather_api_key:
            return self._simulate()

        params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": settings.openweather_api_key,
            "units": "imperial",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            return self._parse_response(data)
        except Exception:
            return self._simulate()

    def _parse_response(self, data: dict) -> WeatherSignalData:
        """Parse OWM response and score weather risk."""
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather = data.get("weather", [{}])[0]

        temp_f = main.get("temp", 70)
        wind_mph = wind.get("speed", 0) * 2.237  # m/s to mph
        description = weather.get("description", "clear")

        risk_factors = []
        score = 0.0

        if temp_f > 95:
            score += 0.3
            risk_factors.append("extreme heat")
        elif temp_f > 85:
            score += 0.15
            risk_factors.append("high heat")

        if wind_mph > 30:
            score += 0.2
            risk_factors.append("high winds")

        if "thunder" in description or "storm" in description:
            score += 0.35
            risk_factors.append("thunderstorm")
        elif "rain" in description:
            score += 0.15
            risk_factors.append("rain")

        return WeatherSignalData(
            score=min(score, 1.0),
            conditions=f"{description.title()}, {temp_f:.0f}°F, {wind_mph:.0f}mph wind",
            temperature_f=temp_f,
            wind_mph=wind_mph,
            risk_factors=risk_factors,
        )

    def _simulate(self) -> WeatherSignalData:
        return WeatherSignalData(
            score=round(random.uniform(0.0, 0.3), 3),
            conditions="Clear, 74°F, 6mph wind",
            temperature_f=74.0,
            wind_mph=6.0,
            risk_factors=[],
        )


class CrowdDensityFetcher:
    """Estimates crowd density from ticketing data."""

    def __init__(self, event_id: str, venue_capacity: int = 20000):
        self.event_id = event_id
        self.venue_capacity = venue_capacity

    async def fetch(self) -> CrowdDensityData:
        """Estimate attendance from Ticketmaster or simulate."""
        if not settings.ticketmaster_key:
            return self._simulate()

        # Ticketmaster API stub — wire up during hackathon Day 1
        return self._simulate()

    def _simulate(self) -> CrowdDensityData:
        pct = random.uniform(0.55, 0.95)
        attendance = int(self.venue_capacity * pct)
        density = pct * 3.5  # rough agents/m² at capacity ~ 3.5

        score = 0.0
        if pct > 0.90:
            score = 0.8
        elif pct > 0.75:
            score = 0.5
        elif pct > 0.60:
            score = 0.3
        else:
            score = 0.1

        return CrowdDensityData(
            score=round(score, 3),
            estimated_attendance=attendance,
            capacity=self.venue_capacity,
            density_per_sqm=round(density, 2),
        )


class TicketVelocityFetcher:
    """Monitors ticket resale velocity as a proxy for crowd mood."""

    def __init__(self, event_id: str):
        self.event_id = event_id

    async def fetch(self) -> TicketVelocityData:
        """Fetch ticket resale data or simulate."""
        # Wire up to StubHub / Ticketmaster resale API during hackathon
        return self._simulate()

    def _simulate(self) -> TicketVelocityData:
        resale_spike = random.random() > 0.7
        score = round(random.uniform(0.3, 0.7) if resale_spike else random.uniform(0.1, 0.4), 3)
        return TicketVelocityData(
            score=score,
            resale_spike=resale_spike,
            walkup_estimate=random.randint(200, 2000),
        )
