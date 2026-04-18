"""Pydantic models for the Iris monitoring module."""

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def score_to_risk_level(score: float) -> RiskLevel:
    """Map a 0–1 composite score to a RiskLevel enum."""
    if score < 0.30:
        return RiskLevel.LOW
    elif score < 0.60:
        return RiskLevel.MODERATE
    elif score < 0.80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


class TwitterSignalData(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    tweet_count: int = 0
    sample_text: str = ""
    trend: str = "stable"  # "increasing" | "stable" | "decreasing"


class WeatherSignalData(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    conditions: str = "Unknown"
    temperature_f: float = 70.0
    wind_mph: float = 0.0
    risk_factors: list[str] = []


class CrowdDensityData(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    estimated_attendance: int = 0
    capacity: int = 0
    density_per_sqm: float = 0.0


class TicketVelocityData(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    resale_spike: bool = False
    walkup_estimate: int = 0


class SignalBundle(BaseModel):
    twitter_sentiment: TwitterSignalData = TwitterSignalData(score=0.0)
    weather: WeatherSignalData = WeatherSignalData(score=0.0)
    crowd_density: CrowdDensityData = CrowdDensityData(score=0.0)
    ticket_velocity: TicketVelocityData = TicketVelocityData(score=0.0)


class IrisStatusResponse(BaseModel):
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel = RiskLevel.LOW
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    signals: SignalBundle = Field(default_factory=SignalBundle)
    alert: Optional[str] = None
    recommendations: list[str] = []


class SignalDataPoint(BaseModel):
    timestamp: datetime
    source: str
    raw_score: float
    data: dict = {}


class SignalFeedResponse(BaseModel):
    event_id: str
    window_minutes: int
    signals: list[SignalDataPoint] = []
