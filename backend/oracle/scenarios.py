"""Scenario definitions and simulation request models."""

from pydantic import BaseModel, Field
from typing import Optional
import json
import os


class CrowdProfile(BaseModel):
    casual: float = 0.40
    friends_group: float = 0.30
    influencer: float = 0.10
    staff: float = 0.15
    non_compliant: float = 0.05


class EventConfig(BaseModel):
    venue_name: str = "Demo Venue"
    capacity: int = 20000
    current_attendance: int = 18000
    venue_width_m: float = 200.0
    venue_height_m: float = 150.0
    exit_count: int = 4
    crowd_profile: CrowdProfile = Field(default_factory=CrowdProfile)


class IncidentConfig(BaseModel):
    type: str = "crowd_surge"
    location: str = "main_stage_pit"
    trigger_time_seconds: int = 180
    severity: str = "high"


class SimulationConfig(BaseModel):
    agent_count: int = Field(default=10000, le=10000)
    duration_seconds: int = Field(default=600, le=600)
    use_claude_reasoning: bool = True


class SimulateRequest(BaseModel):
    scenario_id: str = "concert_general_admission"
    event_config: EventConfig = Field(default_factory=EventConfig)
    incident: IncidentConfig = Field(default_factory=IncidentConfig)
    simulation_config: SimulationConfig = Field(default_factory=SimulationConfig)


def get_built_in_scenarios() -> list[dict]:
    """Return list of built-in scenario descriptors."""
    return [
        {
            "id": "concert_general_admission",
            "name": "Concert: General Admission",
            "description": "High-energy GA floor, 10k–25k capacity",
            "incident_types": ["surge", "medical", "weather", "evacuation"],
        },
        {
            "id": "festival_multi_stage",
            "name": "Festival: Multi-Stage",
            "description": "Large outdoor festival with multiple stages",
            "incident_types": ["surge", "fire", "weather", "crowd_crush"],
        },
        {
            "id": "stadium_sports",
            "name": "Stadium: Sports Event",
            "description": "Seated stadium, 50k–80k capacity",
            "incident_types": ["evacuation", "fight", "medical", "fire"],
        },
    ]


async def run_backtest(event_ids: list[str], simulation_config: dict) -> dict:
    """Run simulations against historical events and compare to known outcomes.

    Loads historical data from data/backtest_events.json.
    """
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "backtest_events.json"
    )

    try:
        with open(data_path) as f:
            historical = {e["id"]: e for e in json.load(f).get("events", [])}
    except FileNotFoundError:
        historical = {}

    results = []
    total_accuracy = 0.0

    for event_id in event_ids:
        event_data = historical.get(event_id)
        if not event_data:
            continue

        # Stub: in hackathon Day 4, wire real simulation results
        predicted_score = event_data.get("predicted_risk_score", 0.75)
        actual = event_data.get("actual_risk_level", "HIGH")
        accuracy = event_data.get("historical_accuracy", 0.91)

        results.append(
            {
                "event_id": event_id,
                "event_name": event_data.get("name", event_id),
                "predicted_risk_score": predicted_score,
                "actual_risk_level": actual,
                "accuracy": accuracy,
                "model_assessment": event_data.get("notes", ""),
            }
        )
        total_accuracy += accuracy

    overall = total_accuracy / len(results) if results else 0.0

    return {
        "backtest_id": f"bt_{hash(tuple(event_ids)) % 100000:05d}",
        "results": results,
        "overall_accuracy": round(overall, 3),
        "target_met": overall >= 0.92,
    }
