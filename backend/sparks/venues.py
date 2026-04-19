"""Venue and event data models for the Sparks entertainment vertical."""

from typing import Optional
from pydantic import BaseModel, Field


class Exit(BaseModel):
    name: str
    location: str
    width_m: float = 3.0
    capacity_per_min: int = 240


class Zone(BaseModel):
    name: str
    location: str
    density_threshold: float = Field(4.5, description="persons/sqm at which zone becomes high-risk")
    risk_level: str = "normal"


class VenueConfig(BaseModel):
    name: str
    location: str
    capacity: int
    venue_type: str = "outdoor_festival"
    has_general_admission: bool = True
    exits: list[Exit] = []
    zones: list[Zone] = []


class EventConfig(BaseModel):
    event_id: str
    event_name: str
    date: str
    location: str
    event_type: str = "festival"
    artist_or_team: str = ""
    expected_attendance: Optional[int] = None
    venue: VenueConfig


# ── Pre-configured events ──────────────────────────────────────────────────

_EVENTS: dict[str, EventConfig] = {
    "astroworld_2024": EventConfig(
        event_id="astroworld_2024",
        event_name="Astroworld Festival 2024",
        date="2024-11-08",
        location="Houston, TX",
        event_type="festival",
        artist_or_team="Travis Scott",
        expected_attendance=45000,
        venue=VenueConfig(
            name="NRG Park",
            location="Houston, TX",
            capacity=50000,
            venue_type="outdoor_festival",
            has_general_admission=True,
            exits=[
                Exit(name="North Gate", location="north", width_m=12, capacity_per_min=960),
                Exit(name="South Gate", location="south", width_m=8, capacity_per_min=640),
                Exit(name="East Tunnel", location="east", width_m=6, capacity_per_min=480),
                Exit(name="West Tunnel", location="west", width_m=6, capacity_per_min=480),
            ],
            zones=[
                Zone(name="Main Stage Pit", location="main_stage", density_threshold=4.0, risk_level="high"),
                Zone(name="South Stage", location="south_stage", density_threshold=4.5, risk_level="normal"),
            ],
        ),
    ),
    "coachella_2023": EventConfig(
        event_id="coachella_2023",
        event_name="Coachella Valley Music Festival 2023",
        date="2023-04-14",
        location="Indio, CA",
        event_type="festival",
        artist_or_team="Bad Bunny (headliner)",
        expected_attendance=112000,
        venue=VenueConfig(
            name="Empire Polo Club",
            location="Indio, CA",
            capacity=125000,
            venue_type="outdoor_festival",
            has_general_admission=True,
            exits=[
                Exit(name="Main Gate", location="north", width_m=20, capacity_per_min=1600),
                Exit(name="Sahara Exit", location="east", width_m=10, capacity_per_min=800),
                Exit(name="Coachella Stage Exit", location="west", width_m=10, capacity_per_min=800),
                Exit(name="Emergency South", location="south", width_m=8, capacity_per_min=640),
            ],
            zones=[
                Zone(name="Coachella Stage", location="main_stage", density_threshold=3.0, risk_level="normal"),
                Zone(name="Sahara Tent", location="sahara_stage", density_threshold=3.5, risk_level="elevated"),
            ],
        ),
    ),
    "super_bowl_58": EventConfig(
        event_id="super_bowl_58",
        event_name="Super Bowl LVIII",
        date="2024-02-11",
        location="Las Vegas, NV",
        event_type="sports",
        artist_or_team="Kansas City Chiefs vs San Francisco 49ers",
        expected_attendance=61629,
        venue=VenueConfig(
            name="Allegiant Stadium",
            location="Las Vegas, NV",
            capacity=65326,
            venue_type="stadium",
            has_general_admission=False,
            exits=[
                Exit(name="North Plaza Exit", location="north", width_m=15, capacity_per_min=1200),
                Exit(name="South Plaza Exit", location="south", width_m=15, capacity_per_min=1200),
                Exit(name="East Gate", location="east", width_m=12, capacity_per_min=960),
                Exit(name="West Gate", location="west", width_m=12, capacity_per_min=960),
                Exit(name="Emergency A", location="northeast", width_m=6, capacity_per_min=480),
                Exit(name="Emergency B", location="southwest", width_m=6, capacity_per_min=480),
            ],
            zones=[
                Zone(name="Lower Bowl", location="lower_seating", density_threshold=5.0, risk_level="normal"),
                Zone(name="Field Level", location="field", density_threshold=6.0, risk_level="normal"),
            ],
        ),
    ),
}


def get_event(event_id: str) -> Optional[EventConfig]:
    return _EVENTS.get(event_id)


def list_all_events() -> dict:
    from sparks.entertainment import EntertainmentScorer, compute_sparks_scores
    events = []
    for eid, ev in _EVENTS.items():
        scorer = EntertainmentScorer(eid)
        factors = scorer._compute_factors(ev)
        scores = compute_sparks_scores(factors)
        from iris.models import score_to_risk_level
        risk_level = score_to_risk_level(factors["composite_risk"])
        events.append({
            "event_id": eid,
            "event_name": ev.event_name,
            "date": ev.date,
            "venue": ev.venue.name,
            "event_type": ev.event_type,
            "composite_risk": factors["composite_risk"],
            "risk_level": risk_level.value,
            "scores": scores,
        })
    return {"events": events, "total": len(events)}
