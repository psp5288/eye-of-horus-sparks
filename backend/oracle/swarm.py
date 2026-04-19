"""Swarm simulation engine: 10,000 agent-based crowd simulation."""

import asyncio
import logging
import random
import time
from typing import Optional

import numpy as np

from oracle.agents import Agent, AgentArchetype, ARCHETYPE_PARAMS
from oracle.scenarios import Scenario

logger = logging.getLogger(__name__)

# Simulation constants
DEFAULT_AGENTS = 10_000
TICKS_PER_SECOND = 2          # dt = 0.5s
CLAUDE_CALL_INTERVAL = 50     # ticks between Claude agent-behavior calls
CLAUDE_SAMPLE_SIZE = 10       # agents sampled per Claude call


class SwarmSimulation:
    """
    10,000-agent crowd simulation using NumPy physics + Claude reasoning.

    Agents are distributed across the venue grid. Each tick:
    1. Physics update: update velocity/position from panic + density forces
    2. Every 50 ticks: sample 10 agents → ask Claude for behavior decisions
    3. Apply Claude's decisions as velocity/panic overrides

    Parameters
    ----------
    num_agents : int
        Population size (default 10,000).
    event_id : str
        Event identifier — used to load venue geometry and archetype distribution.
    """

    def __init__(self, num_agents: int = DEFAULT_AGENTS, event_id: str = "coachella_2023") -> None:
        self.num_agents = num_agents
        self.event_id = event_id
        self.agents: list[Agent] = []
        self.tick = 0
        self._history: list[dict] = []

    def initialize_agents(self, archetype_distribution: Optional[dict] = None) -> None:
        """
        Spawn agents with archetype distribution and random initial positions.

        Parameters
        ----------
        archetype_distribution : dict | None
            {archetype_value: fraction} — defaults to festival distribution.
        """
        if archetype_distribution is None:
            archetype_distribution = {
                "casual": 0.40, "friends_group": 0.28,
                "influencer": 0.15, "staff": 0.12, "non_compliant": 0.05,
            }

        archetype_map = {a.value: a for a in AgentArchetype}
        self.agents = []
        agent_id = 0

        for archetype_val, fraction in archetype_distribution.items():
            count = int(self.num_agents * fraction)
            archetype = archetype_map.get(archetype_val, AgentArchetype.CASUAL_ATTENDEE)
            for _ in range(count):
                self.agents.append(Agent(
                    id=agent_id,
                    archetype=archetype,
                    x=random.gauss(0.5, 0.2),  # cluster near stage
                    y=random.uniform(0.1, 0.9),
                    panic_level=0.0,
                    state="idle",
                ))
                agent_id += 1

        logger.info("Initialized %d agents for event %s", len(self.agents), self.event_id)

    async def run_simulation(
        self,
        scenario: Scenario,
        num_ticks: int = 300,
        use_claude: bool = True,
    ) -> dict:
        """
        Execute the simulation and return predictions.

        Parameters
        ----------
        scenario : Scenario
            Incident scenario to simulate.
        num_ticks : int
            Total simulation ticks (300 ticks × 0.5s = 150 seconds).
        use_claude : bool
            If True, call Claude every CLAUDE_CALL_INTERVAL ticks.

        Returns
        -------
        dict
            evacuation_time_seconds, peak_density, bottlenecks, agent_outcomes,
            crowd_sentiment_trajectory, estimated_injury_risk, scores.
        """
        start_time = time.time()
        self.initialize_agents()

        trigger_tick = scenario.trigger_time_s * TICKS_PER_SECOND
        incident_active = False
        sentiment_trajectory = []
        peak_density = 0.0

        for tick in range(num_ticks):
            self.tick = tick
            incident_active = tick >= trigger_tick

            environment = {
                "incident_active": incident_active,
                "incident_type": scenario.incident_type,
                "incident_intensity": {"low": 0.2, "medium": 0.5, "high": 0.9}.get(scenario.severity, 0.5),
                "elapsed_time_s": tick / TICKS_PER_SECOND,
                "event_id": self.event_id,
            }

            # Physics update
            self._tick_physics(environment)

            # Claude agent behavior (every 50 ticks, when incident active)
            if use_claude and incident_active and tick % CLAUDE_CALL_INTERVAL == 0:
                sample = random.sample(self.agents, min(CLAUDE_SAMPLE_SIZE, len(self.agents)))
                await self._apply_claude_behavior(sample, environment)

            # Track density
            density = self._compute_density()
            peak_density = max(peak_density, density)

            # Track sentiment
            if tick % 25 == 0:
                avg_panic = sum(a.panic_level for a in self.agents) / len(self.agents)
                sentiment_trajectory.append(round(1.0 - avg_panic, 3))

            # Snapshot for Claude history
            if tick % 50 == 0:
                self._history.append({"tick": tick, "density": round(density, 3), "incident_active": incident_active})

        sim_time = time.time() - start_time
        results = self._compile_results(scenario, sentiment_trajectory, peak_density, sim_time)
        return results

    def _tick_physics(self, environment: dict) -> None:
        """Apply physics rules to all agents for one tick."""
        incident_active = environment.get("incident_active", False)
        intensity = environment.get("incident_intensity", 0.3)

        for agent in self.agents:
            neighbors = self._get_neighbors(agent, radius=0.05)
            agent.update(neighbors, environment)

            # Move evacuating agents toward exits (simplified: top edge = exit)
            if agent.state in ("evacuating", "panicking"):
                agent.vy -= 0.01 * (1 + agent.panic_level)
                agent.vx += random.gauss(0, 0.005)

            # Apply velocity with damping
            agent.x = max(0.0, min(1.0, agent.x + agent.vx))
            agent.y = max(0.0, min(1.0, agent.y + agent.vy))
            agent.vx *= 0.85
            agent.vy *= 0.85

    def _get_neighbors(self, agent: Agent, radius: float = 0.05) -> list[Agent]:
        """Return agents within radius of given agent (simplified O(n) — production uses KD-tree)."""
        neighbors = []
        for other in self.agents:
            if other.id != agent.id:
                dist = ((other.x - agent.x) ** 2 + (other.y - agent.y) ** 2) ** 0.5
                if dist < radius:
                    neighbors.append(other)
        return neighbors[:8]  # cap to 8 nearest for perf

    def _compute_density(self) -> float:
        """Estimate average crowd density as fraction of agents in high-density zone."""
        stage_zone = sum(1 for a in self.agents if a.x > 0.3 and a.x < 0.7 and a.y < 0.3)
        return stage_zone / max(len(self.agents), 1)

    async def _apply_claude_behavior(self, sample: list[Agent], environment: dict) -> None:
        """Ask Claude for behavioral decisions and apply to sampled agents."""
        from oracle.claude_integration import generate_agent_behavior
        decisions = await generate_agent_behavior(
            [a.to_dict() for a in sample],
            environment,
            self._history[-3:] if self._history else None,
        )
        agent_map = {a.id: a for a in sample}
        for decision in decisions:
            agent = agent_map.get(decision.get("agent_id"))
            if agent:
                agent.panic_level = float(decision.get("panic_level", agent.panic_level))
                action = decision.get("action", "")
                if action == "move_toward_exit":
                    agent.state = "evacuating"
                elif action == "obstruct_flow":
                    agent.state = "obstructing"

    def _compile_results(
        self,
        scenario: Scenario,
        sentiment_trajectory: list[float],
        peak_density: float,
        sim_time: float,
    ) -> dict:
        """Compile final results dict from simulation state."""
        evacuated = sum(1 for a in self.agents if a.y > 0.9)
        panicking = sum(1 for a in self.agents if a.state == "panicking")
        injured = max(0, int(panicking * 0.02 * {"low": 0.3, "medium": 0.7, "high": 1.5}.get(scenario.severity, 1.0)))
        at_risk = panicking

        # Simplified evacuation time estimate
        evacuation_time_s = int(300 + panicking * 0.05 + (1 - evacuated / len(self.agents)) * 600)

        bottlenecks = []
        if peak_density > 0.15:
            bottlenecks.append({"location": "main_stage_barrier", "peak_pressure": round(peak_density * 10, 1), "risk_score": round(peak_density * 8, 1)})
        if at_risk > self.num_agents * 0.05:
            bottlenecks.append({"location": "north_exit_tunnel", "peak_pressure": round(at_risk / self.num_agents * 8, 1), "risk_score": 5.0})

        return {
            "event_id": self.event_id,
            "simulation_time_s": round(sim_time, 2),
            "predictions": {
                "evacuation_time_seconds": evacuation_time_s,
                "peak_density": round(peak_density, 4),
                "estimated_injury_risk": round(injured / max(len(self.agents), 1), 4),
                "bottlenecks": bottlenecks,
                "agent_outcomes": {
                    "total": len(self.agents),
                    "safely_evacuated": evacuated,
                    "at_risk": at_risk,
                    "injured": injured,
                },
                "crowd_sentiment_trajectory": sentiment_trajectory,
            },
        }

    def get_results(self) -> dict:
        """Return summary of last simulation (if run externally)."""
        return {
            "tick": self.tick,
            "agent_count": len(self.agents),
            "avg_panic": round(sum(a.panic_level for a in self.agents) / max(len(self.agents), 1), 3),
        }
