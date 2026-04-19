"""Pydantic models for the Iris monitoring module."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def score_to_risk_level(score: float) -> RiskLevel:
    if score < 0.30:
        return RiskLevel.LOW
    elif score < 0.60:
        return RiskLevel.MODERATE
    elif score < 0.80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


class TwitterSignal(BaseModel):
    sentiment_score: float = Field(0.5, ge=0.0, le=1.0, description="0=negative, 1=positive")
    sample_text: str = ""
    tweet_volume: int = 0
    raw_score: float = 0.5


class WeatherSignal(BaseModel):
    temperature_f: float = 72.0
    humidity_pct: float = 50.0
    conditions: str = "Clear"
    wind_mph: float = 0.0
    risk_score: float = Field(0.1, ge=0.0, le=1.0)


class CrowdDensitySignal(BaseModel):
    density_score: float = Field(0.5, ge=0.0, le=1.0)
    density_per_sqm: float = 2.0
    hotspots: List[str] = []


class TicketingSignal(BaseModel):
    velocity_score: float = Field(0.4, ge=0.0, le=1.0)
    resale_spike: bool = False
    resale_premium_pct: float = 0.0


class SignalBundle(BaseModel):
    event_id: str
    timestamp: datetime
    twitter: TwitterSignal = TwitterSignal()
    weather: WeatherSignal = WeatherSignal()
    crowd_density: CrowdDensitySignal = CrowdDensitySignal()
    ticket_velocity: TicketingSignal = TicketingSignal()


class RiskScore(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Composite risk 0–1")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in score 0–1")
    level: RiskLevel
    breakdown: dict = {}


class EventData(BaseModel):
    event_id: str
    event_name: str
    date: str
    venue: str
    location: str
    capacity: int
    event_type: str = "festival"
    expected_attendance: Optional[int] = None
