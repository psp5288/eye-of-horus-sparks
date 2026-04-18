"""Venue and event data models for the Sparks entertainment vertical."""

from pydantic import BaseModel
from typing import Optional
from datetime import date


class Venue(BaseModel):
    id: str
    name: str
    city: str
    state: str
    capacity: int
    venue_type: str  # "indoor_arena" | "outdoor_festival" | "stadium" | "amphitheater"
    lat: float = 0.0
    lon: float = 0.0
    exit_count: int = 4
    has_general_admission: bool = True


class EventConfig(BaseModel):
    id: str
    name: str
    venue: Venue
    event_date: str
    event_type: str  # "concert" | "festival" | "sports" | "conference"
    expected_attendance: int
    artist_or_team: Optional[str] = None
    status: str = "upcoming"  # "upcoming" | "active" | "completed"


# In-memory event registry (replace with DB in production)
_EVENTS: list[EventConfig] = [
    EventConfig(
        id="coachella_2025_w1",
        name="Coachella 2025 - Weekend 1",
        venue=Venue(
            id="empire_polo_club",
            name="Empire Polo Club",
            city="Indio",
            state="CA",
            capacity=125000,
            venue_type="outdoor_festival",
            lat=33.6826,
            lon=-116.2373,
            exit_count=12,
            has_general_admission=True,
        ),
        event_date="2025-04-18",
        event_type="festival",
        expected_attendance=110000,
        artist_or_team="Various",
        status="active",
    ),
    EventConfig(
        id="demo_event",
        name="Demo Concert",
        venue=Venue(
            id="demo_venue",
            name="Demo Arena",
            city="San Francisco",
            state="CA",
            capacity=20000,
            venue_type="indoor_arena",
            lat=37.7749,
            lon=-122.4194,
            exit_count=6,
            has_general_admission=True,
        ),
        event_date="2025-04-21",
        event_type="concert",
        expected_attendance=18000,
        artist_or_team="Demo Artist",
        status="upcoming",
    ),
]


def list_events() -> list[dict]:
    """Return all configured events as dicts."""
    return [e.model_dump() for e in _EVENTS]


def get_event(event_id: str) -> Optional[EventConfig]:
    """Return a specific event by ID."""
    return next((e for e in _EVENTS if e.id == event_id), None)
