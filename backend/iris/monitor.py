"""IrisMonitor: aggregates all signals in parallel and returns IrisStatus."""

import asyncio
import logging
from datetime import datetime, timezone

from iris.models import SignalBundle, RiskScore, score_to_risk_level
from iris.signals import fetch_twitter_signal, fetch_weather_signal, fetch_crowd_density_signal, fetch_ticketing_signal
from iris.scorer import compute_risk_score

logger = logging.getLogger(__name__)


class IrisMonitor:
    """Orchestrates signal ingestion and risk scoring for a live event."""

    def __init__(self) -> None:
        self._cache: dict = {}

    async def fetch_signals(self, event_id: str) -> dict:
        """
        Aggregate signals from all sources and return the full status bundle.

        Parameters
        ----------
        event_id : str
            Event identifier (e.g. 'coachella_2023').

        Returns
        -------
        dict
            Full signal bundle + composite risk score + Claude interpretation.
        """
        logger.info("Fetching signals for event: %s", event_id)

        twitter, weather, density, ticketing = await asyncio.gather(
            fetch_twitter_signal(event_id),
            fetch_weather_signal(event_id),
            fetch_crowd_density_signal(event_id),
            fetch_ticketing_signal(event_id),
            return_exceptions=True,
        )

        # Replace exceptions with defaults
        from iris.models import TwitterSignal, WeatherSignal, CrowdDensitySignal, TicketingSignal
        twitter   = twitter   if not isinstance(twitter,   Exception) else TwitterSignal()
        weather   = weather   if not isinstance(weather,   Exception) else WeatherSignal()
        density   = density   if not isinstance(density,   Exception) else CrowdDensitySignal()
        ticketing = ticketing if not isinstance(ticketing, Exception) else TicketingSignal()

        bundle = SignalBundle(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            twitter=twitter,
            weather=weather,
            crowd_density=density,
            ticket_velocity=ticketing,
        )

        risk = compute_risk_score(bundle)

        return {
            "event_id": event_id,
            "timestamp": bundle.timestamp.isoformat(),
            "signals": {
                "twitter": bundle.twitter.model_dump(),
                "weather": bundle.weather.model_dump(),
                "crowd_density": bundle.crowd_density.model_dump(),
                "ticket_velocity": bundle.ticket_velocity.model_dump(),
            },
            "composite_risk": round(risk.score, 3),
            "risk_level": risk.level.value,
            "confidence": round(risk.confidence, 3),
            "breakdown": risk.breakdown,
        }

    async def start_polling(self, event_id: str, interval_s: int = 30) -> None:
        """Poll signals on a fixed interval (background task)."""
        while True:
            try:
                await self.fetch_signals(event_id)
            except Exception as exc:
                logger.error("Poll error for %s: %s", event_id, exc)
            await asyncio.sleep(interval_s)
