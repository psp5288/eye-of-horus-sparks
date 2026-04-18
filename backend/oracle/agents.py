"""Agent archetype definitions for the swarm simulation."""

from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class AgentArchetype(str, Enum):
    CASUAL = "casual"
    FRIENDS_GROUP = "friends_group"
    INFLUENCER = "influencer"
    STAFF = "staff"
    NON_COMPLIANT = "non_compliant"


@dataclass
class ArchetypeProfile:
    """Behavioral parameters for an agent archetype."""

    name: AgentArchetype
    base_speed: float          # meters/tick (1 tick = 1 second)
    panic_threshold: float     # crowd_pressure at which panic behavior starts (0–1)
    compliance: float          # probability of following instructions (0–1)
    social_influence: float    # how much this agent affects neighbors (0–1)
    group_size: int            # average group size (1 = solo)
    color: str                 # for visualization

    def speed_with_modifier(self, modifier: float = 1.0) -> float:
        return max(0.0, min(self.base_speed * modifier, 5.0))


# Pre-defined archetype profiles
ARCHETYPES: dict[AgentArchetype, ArchetypeProfile] = {
    AgentArchetype.CASUAL: ArchetypeProfile(
        name=AgentArchetype.CASUAL,
        base_speed=1.2,
        panic_threshold=0.65,
        compliance=0.85,
        social_influence=0.20,
        group_size=2,
        color="#4a90d9",
    ),
    AgentArchetype.FRIENDS_GROUP: ArchetypeProfile(
        name=AgentArchetype.FRIENDS_GROUP,
        base_speed=1.0,
        panic_threshold=0.55,
        compliance=0.75,
        social_influence=0.45,
        group_size=5,
        color="#7ed321",
    ),
    AgentArchetype.INFLUENCER: ArchetypeProfile(
        name=AgentArchetype.INFLUENCER,
        base_speed=1.4,
        panic_threshold=0.70,
        compliance=0.65,
        social_influence=0.80,
        group_size=1,
        color="#f5a623",
    ),
    AgentArchetype.STAFF: ArchetypeProfile(
        name=AgentArchetype.STAFF,
        base_speed=1.8,
        panic_threshold=0.95,
        compliance=1.00,
        social_influence=0.60,
        group_size=1,
        color="#ffffff",
    ),
    AgentArchetype.NON_COMPLIANT: ArchetypeProfile(
        name=AgentArchetype.NON_COMPLIANT,
        base_speed=1.5,
        panic_threshold=0.45,
        compliance=0.15,
        social_influence=0.35,
        group_size=3,
        color="#d0021b",
    ),
}


@dataclass
class Agent:
    """A single simulation agent."""

    id: int
    archetype: AgentArchetype
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    panic_level: float = 0.0      # 0 (calm) to 1 (full panic)
    evacuated: bool = False
    at_risk: bool = False
    speed_modifier: float = 1.0

    @property
    def profile(self) -> ArchetypeProfile:
        return ARCHETYPES[self.archetype]

    def update_panic(self, local_pressure: float) -> None:
        """Update panic level based on local crowd pressure."""
        threshold = self.profile.panic_threshold
        if local_pressure > threshold:
            increase = (local_pressure - threshold) * 0.1
            self.panic_level = min(1.0, self.panic_level + increase)
        else:
            self.panic_level = max(0.0, self.panic_level - 0.02)

    def apply_behavior(self, action: str, speed_modifier: float, panic_level: float) -> None:
        """Apply behavior from Claude reasoning."""
        self.speed_modifier = speed_modifier
        self.panic_level = panic_level


def create_agent_population(
    n: int,
    crowd_profile: dict[str, float],
    venue_width: float,
    venue_height: float,
    rng: np.random.Generator,
) -> list[Agent]:
    """Create N agents distributed across the venue according to crowd_profile.

    crowd_profile: {"casual": 0.40, "friends_group": 0.30, ...} — must sum to ~1.0
    """
    archetype_map = {
        "casual": AgentArchetype.CASUAL,
        "friends_group": AgentArchetype.FRIENDS_GROUP,
        "influencer": AgentArchetype.INFLUENCER,
        "staff": AgentArchetype.STAFF,
        "non_compliant": AgentArchetype.NON_COMPLIANT,
    }

    agents = []
    agent_id = 0

    for archetype_key, fraction in crowd_profile.items():
        count = int(n * fraction)
        archetype = archetype_map.get(archetype_key, AgentArchetype.CASUAL)

        xs = rng.uniform(0, venue_width, count)
        ys = rng.uniform(0, venue_height, count)

        for i in range(count):
            agents.append(
                Agent(
                    id=agent_id,
                    archetype=archetype,
                    x=float(xs[i]),
                    y=float(ys[i]),
                )
            )
            agent_id += 1

    return agents
