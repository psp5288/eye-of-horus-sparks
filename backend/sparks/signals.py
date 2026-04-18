"""Entertainment-specific signal definitions for the Sparks vertical."""

import random
from dataclasses import dataclass


@dataclass
class SocialBuzzSignal:
    """Social media buzz intensity for an artist/event."""
    event_id: str
    buzz_score: float        # 0–1, higher = more viral/trending
    mention_count: int
    sentiment_positive: float
    top_platform: str        # "twitter" | "tiktok" | "instagram"

    @classmethod
    def simulate(cls, event_id: str) -> "SocialBuzzSignal":
        score = round(random.uniform(0.4, 0.95), 3)
        return cls(
            event_id=event_id,
            buzz_score=score,
            mention_count=random.randint(5000, 200000),
            sentiment_positive=round(random.uniform(0.6, 0.95), 3),
            top_platform=random.choice(["twitter", "tiktok", "instagram"]),
        )


@dataclass
class TicketResaleSignal:
    """Ticket resale market conditions — proxy for crowd demand pressure."""
    event_id: str
    resale_premium_pct: float    # % above face value on resale market
    volume_24h: int              # number of resale listings in last 24h
    panic_sell_detected: bool    # sudden drop in resale price

    @classmethod
    def simulate(cls, event_id: str) -> "TicketResaleSignal":
        premium = round(random.uniform(10, 250), 1)
        return cls(
            event_id=event_id,
            resale_premium_pct=premium,
            volume_24h=random.randint(50, 3000),
            panic_sell_detected=random.random() > 0.85,
        )


@dataclass
class ArtistAnnouncementSignal:
    """Tracks surprise artist announcements that can cause crowd surges."""
    event_id: str
    announced: bool
    announcement_time: str
    expected_surge_pct: float    # estimated % of crowd that will move toward stage

    @classmethod
    def simulate(cls, event_id: str) -> "ArtistAnnouncementSignal":
        announced = random.random() > 0.7
        return cls(
            event_id=event_id,
            announced=announced,
            announcement_time="21:45" if announced else "",
            expected_surge_pct=round(random.uniform(0.15, 0.45), 3) if announced else 0.0,
        )
