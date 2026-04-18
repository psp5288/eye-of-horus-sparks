"""IrisMonitor: aggregates all signals in parallel and returns IrisStatus."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from iris.models import (
    IrisStatusResponse,
    SignalBundle,
    SignalFeedResponse,
    SignalDataPoint,
)
from iris.signals import (
    TwitterSignalFetcher,
    WeatherSignalFetcher,
    CrowdDensityFetcher,
    TicketVelocityFetcher,
)
from iris.scorer import RiskScorer

# In-memory cache per event_id: {"event_id": (timestamp, IrisStatusResponse)}
_status_cache: dict[str, tuple[datetime, IrisStatusResponse]] = {}
_CACHE_TTL_SECONDS = 30


class IrisMonitor:
    """Collects and aggregates real-time signals for an event."""

    def __init__(self, event_id: str, venue_capacity: int = 20000):
        self.event_id = event_id
        self.venue_capacity = venue_capacity
        self.scorer = RiskScorer()

    async def get_status(self) -> IrisStatusResponse:
        """Return current risk status. Uses 30s cache to avoid rate limits."""
        cached = _status_cache.get(self.event_id)
        if cached:
            timestamp, status = cached
            if (datetime.utcnow() - timestamp).seconds < _CACHE_TTL_SECONDS:
                return status

        status = await self._collect_and_score()
        _status_cache[self.event_id] = (datetime.utcnow(), status)
        return status

    async def _collect_and_score(self) -> IrisStatusResponse:
        """Fetch all signals concurrently, then score."""
        twitter_fetcher = TwitterSignalFetcher(event_id=self.event_id)
        weather_fetcher = WeatherSignalFetcher()
        density_fetcher = CrowdDensityFetcher(
            event_id=self.event_id, venue_capacity=self.venue_capacity
        )
        velocity_fetcher = TicketVelocityFetcher(event_id=self.event_id)

        twitter, weather, density, velocity = await asyncio.gather(
            twitter_fetcher.fetch(),
            weather_fetcher.fetch(),
            density_fetcher.fetch(),
            velocity_fetcher.fetch(),
        )

        signals = SignalBundle(
            twitter_sentiment=twitter,
            weather=weather,
            crowd_density=density,
            ticket_velocity=velocity,
        )

        risk_score, confidence = self.scorer.compute(signals)
        risk_level = self.scorer.get_risk_level(risk_score)
        recommendations = self.scorer.get_recommendations(risk_score, signals)

        return IrisStatusResponse(
            event_id=self.event_id,
            timestamp=datetime.utcnow(),
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            signals=signals,
            alert=recommendations[0] if risk_score >= 0.60 else None,
            recommendations=recommendations,
        )

    async def get_signal_feed(
        self, window_minutes: int = 60
    ) -> SignalFeedResponse:
        """Return a feed of historical signal data points.

        For MVP, returns the current snapshot repeated as a single entry.
        Wire up to a time-series store (InfluxDB / TimescaleDB) during hackathon.
        """
        status = await self.get_status()
        now = datetime.utcnow()

        points = []
        for source, score in [
            ("twitter", status.signals.twitter_sentiment.score),
            ("weather", status.signals.weather.score),
            ("crowd_density", status.signals.crowd_density.score),
            ("ticket_velocity", status.signals.ticket_velocity.score),
        ]:
            points.append(
                SignalDataPoint(
                    timestamp=now,
                    source=source,
                    raw_score=score,
                    data={},
                )
            )

        return SignalFeedResponse(
            event_id=self.event_id,
            window_minutes=window_minutes,
            signals=points,
        )
