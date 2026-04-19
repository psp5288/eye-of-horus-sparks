"""Scenario definitions and simulation request models."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class Scenario(BaseModel):
    """A simulation scenario defining an incident type, timing, and parameters."""
    name: str = "Custom Scenario"
    description: str = ""
    incident_type: str = Field(
        "crowd_surge",
        description="One of: crowd_surge|medical|fire|weather|evacuation|fight",
    )
    trigger_time_s: int = Field(1800, ge=0, le=7200, description="Seconds into event when incident triggers")
    severity: str = Field("medium", description="low|medium|high")
    parameters: dict[str, Any] = {}


SCENARIO_TEMPLATES: dict[str, Scenario] = {
    "stage_rush": Scenario(
        name="Stage Rush",
        description="Fans surge toward stage after surprise announcement.",
        incident_type="crowd_surge",
        trigger_time_s=1800,
        severity="high",
        parameters={"surge_multiplier": 2.0, "origin": "main_stage"},
    ),
    "medical_cluster": Scenario(
        name="Medical Emergency Cluster",
        description="Multiple heat-related medical incidents near centre crowd.",
        incident_type="medical",
        trigger_time_s=900,
        severity="medium",
        parameters={"affected_radius_m": 30, "incident_count": 4},
    ),
    "controlled_evacuation": Scenario(
        name="Controlled Evacuation",
        description="Orderly evacuation drill with low-urgency PA announcement.",
        incident_type="evacuation",
        trigger_time_s=3600,
        severity="low",
        parameters={"announcement_delay_s": 60, "staff_directed": True},
    ),
    "weather_emergency": Scenario(
        name="Severe Weather",
        description="Sudden storm forces evacuation of outdoor areas.",
        incident_type="weather",
        trigger_time_s=2400,
        severity="high",
        parameters={"wind_speed_mph": 45, "lightning_detected": True},
    ),
    "fight_at_barrier": Scenario(
        name="Barrier Altercation",
        description="Fight breaks out near main stage barrier, causing local panic.",
        incident_type="fight",
        trigger_time_s=5400,
        severity="medium",
        parameters={"involved_agents": 15, "location": "main_stage_barrier"},
    ),
}


def parse_scenario_input(input_dict: dict) -> Scenario:
    """
    Parse a scenario from a raw request dict.

    Parameters
    ----------
    input_dict : dict
        Raw scenario parameters from API request.

    Returns
    -------
    Scenario
        Parsed and validated scenario object.
    """
    if not input_dict:
        return SCENARIO_TEMPLATES["stage_rush"]

    template_key = input_dict.get("template")
    if template_key and template_key in SCENARIO_TEMPLATES:
        return SCENARIO_TEMPLATES[template_key]

    return Scenario(**{k: v for k, v in input_dict.items() if k in Scenario.model_fields})


def create_scenario_from_params(
    event_id: str,
    incident_type: str = "crowd_surge",
    severity: str = "medium",
    trigger_time_s: int = 1800,
    parameters: Optional[dict] = None,
) -> Scenario:
    """
    Build a scenario object from explicit parameters.

    Parameters
    ----------
    event_id : str
        Event identifier (used for context; not stored in scenario).
    incident_type : str
    severity : str
    trigger_time_s : int
    parameters : dict | None

    Returns
    -------
    Scenario
    """
    return Scenario(
        name=f"{incident_type.replace('_', ' ').title()} — {event_id}",
        incident_type=incident_type,
        severity=severity,
        trigger_time_s=trigger_time_s,
        parameters=parameters or {},
    )
