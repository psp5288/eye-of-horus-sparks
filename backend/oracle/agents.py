"""Agent archetype definitions for the swarm simulation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AgentArchetype(str, Enum):
    """
    Five crowd archetypes calibrated from Astroworld 2021 OSHA investigation.

    Compliance = probability of following staff/PA instructions.
    Influence  = radius of behavioral contagion (how many nearby agents they affect).
    """
    CASUAL_ATTENDEE = "casual"
    FRIENDS_GROUP   = "friends_group"
    INFLUENCER      = "influencer"
    STAFF           = "staff"
    NON_COMPLIANT   = "non_compliant"


# Archetype parameters — tuned against backtest data
ARCHETYPE_PARAMS: dict[AgentArchetype, dict] = {
    AgentArchetype.CASUAL_ATTENDEE: {
        "share": 0.50,
        "compliance": 0.85,
        "influence_radius": 0.2,
        "panic_threshold": 0.70,
        "movement_speed": 1.0,
        "goal": "enjoy_event",
    },
    AgentArchetype.FRIENDS_GROUP: {
        "share": 0.25,
        "compliance": 0.80,
        "influence_radius": 0.4,
        "panic_threshold": 0.65,
        "movement_speed": 0.9,
        "goal": "stay_together",
    },
    AgentArchetype.INFLUENCER: {
        "share": 0.15,
        "compliance": 0.50,
        "influence_radius": 0.9,
        "panic_threshold": 0.55,
        "movement_speed": 1.2,
        "goal": "content_creation",
    },
    AgentArchetype.STAFF: {
        "share": 0.05,
        "compliance": 1.00,
        "influence_radius": 1.0,
        "panic_threshold": 0.10,
        "movement_speed": 1.5,
        "goal": "manage_crowd",
    },
    AgentArchetype.NON_COMPLIANT: {
        "share": 0.05,
        "compliance": 0.10,
        "influence_radius": 0.6,
        "panic_threshold": 0.40,
        "movement_speed": 1.8,
        "goal": "resist_direction",
    },
}


@dataclass
class Agent:
    """
    Single simulation agent with position, archetype, and behavioral state.

    Attributes
    ----------
    id : int
    archetype : AgentArchetype
    x, y : float  — position in venue (normalised 0–1)
    vx, vy : float — velocity
    panic_level : float — 0 (calm) to 1 (full panic)
    state : str — one of: idle, moving, panicking, evacuating, injured
    """
    id: int
    archetype: AgentArchetype
    x: float = 0.5
    y: float = 0.5
    vx: float = 0.0
    vy: float = 0.0
    panic_level: float = 0.0
    state: str = "idle"
    target_x: Optional[float] = None
    target_y: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "archetype": self.archetype.value,
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "panic_level": round(self.panic_level, 3),
            "state": self.state,
        }

    def update(self, neighbors: list["Agent"], environment: dict) -> None:
        """
        Update agent state based on neighbors and environment.

        Physics rules (pre-Claude):
        - If nearby agent panics and this agent is susceptible → increase panic
        - Non-compliant agents ignore exit directions
        - Staff agents move toward incident zone

        Claude override: every 50 ticks, generate_agent_behavior() replaces
        this rule-based logic for a sampled subset.

        Parameters
        ----------
        neighbors : list[Agent]
            Agents within influence radius.
        environment : dict
            Current incident state, elapsed time, venue geometry.
        """
        params = ARCHETYPE_PARAMS[self.archetype]
        incident_active = environment.get("incident_active", False)

        # Panic contagion from neighbors
        if neighbors:
            avg_neighbor_panic = sum(n.panic_level for n in neighbors) / len(neighbors)
            contagion = avg_neighbor_panic * (1.0 - params["compliance"]) * 0.1
            self.panic_level = min(1.0, self.panic_level + contagion)

        # Incident effect
        if incident_active:
            intensity = environment.get("incident_intensity", 0.3)
            if self.archetype == AgentArchetype.NON_COMPLIANT:
                self.panic_level = min(1.0, self.panic_level + intensity * 0.15)
            elif self.archetype == AgentArchetype.STAFF:
                self.state = "managing"
                self.panic_level = max(0.0, self.panic_level - 0.05)
            else:
                self.panic_level = min(1.0, self.panic_level + intensity * params["compliance"] * 0.05)

        # State transitions
        if self.panic_level > params["panic_threshold"]:
            self.state = "panicking"
        elif incident_active and self.panic_level > 0.3:
            self.state = "evacuating"

    def decide_action(self) -> str:
        """
        Rule-based action decision (placeholder — Claude overrides this in simulation).

        Returns
        -------
        str
            One of: move_toward_exit, hold_position, follow_crowd,
            assist_others, obstruct_flow, seek_information
        """
        if self.archetype == AgentArchetype.STAFF:
            return "assist_others"
        if self.archetype == AgentArchetype.NON_COMPLIANT:
            return "obstruct_flow"
        if self.panic_level > 0.5:
            return "move_toward_exit"
        return "hold_position"
