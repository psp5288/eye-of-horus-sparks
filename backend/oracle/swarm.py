"""Swarm simulation engine: 10,000 agent-based crowd simulation."""

import asyncio
import time
import uuid
import numpy as np
from typing import Optional

from oracle.agents import Agent, create_agent_population, ARCHETYPES
from oracle.scenarios import SimulateRequest
from oracle.claude_integration import ClaudeIntegration
from config import Settings


class SwarmSimulation:
    """Runs an agent-based crowd simulation for a given event scenario."""

    TICK_DURATION = 1.0       # seconds per simulation tick
    CLAUDE_INTERVAL = 50      # call Claude every N ticks
    PRESSURE_RADIUS = 2.5     # meters — radius for local density calculation
    PANIC_SPREAD_RATE = 0.15  # how fast panic propagates between neighbors

    def __init__(self, request: SimulateRequest, settings: Settings):
        self.request = request
        self.settings = settings
        self.rng = np.random.default_rng(seed=42)
        self.claude = ClaudeIntegration()

        self.width = request.event_config.venue_width_m
        self.height = request.event_config.venue_height_m
        self.exits = self._place_exits()

    def _place_exits(self) -> list[tuple[float, float]]:
        """Evenly space exits around the perimeter."""
        n = self.request.event_config.exit_count
        perimeter = 2 * (self.width + self.height)
        spacing = perimeter / n
        exits = []
        for i in range(n):
            d = i * spacing
            if d < self.width:
                exits.append((d, 0.0))
            elif d < self.width + self.height:
                exits.append((self.width, d - self.width))
            elif d < 2 * self.width + self.height:
                exits.append((self.width - (d - self.width - self.height), self.height))
            else:
                exits.append((0.0, self.height - (d - 2 * self.width - self.height)))
        return exits

    async def run(self) -> dict:
        """Execute the simulation and return a result dict."""
        sim_id = f"sim_{uuid.uuid4().hex[:8]}"
        t_start = time.time()

        cfg = self.request.simulation_config
        event_cfg = self.request.event_config
        incident = self.request.incident

        # Initialize agents
        agents = create_agent_population(
            n=cfg.agent_count,
            crowd_profile=event_cfg.crowd_profile.model_dump(),
            venue_width=self.width,
            venue_height=self.height,
            rng=self.rng,
        )

        positions = np.array([[a.x, a.y] for a in agents], dtype=np.float32)
        velocities = np.zeros_like(positions)
        panic_levels = np.zeros(len(agents), dtype=np.float32)

        incident_triggered = False
        evacuation_started = False
        evacuation_tick: Optional[int] = None
        all_evacuated_tick: Optional[int] = None

        bottleneck_data: list[dict] = []
        sentiment_trajectory: list[float] = []

        total_ticks = cfg.duration_seconds

        for tick in range(total_ticks):
            # Trigger incident
            if tick == incident.trigger_time_seconds and not incident_triggered:
                incident_triggered = True
                evacuation_started = True
                evacuation_tick = tick
                self._trigger_incident(agents, positions, panic_levels, incident)

            # Physics update
            positions, velocities, panic_levels = self._update_physics(
                agents, positions, velocities, panic_levels, evacuation_started
            )

            # Mark evacuated agents
            newly_evacuated = self._mark_evacuated(agents, positions)

            # Every CLAUDE_INTERVAL ticks: sample agents and call Claude
            if (
                cfg.use_claude_reasoning
                and tick % self.CLAUDE_INTERVAL == 0
                and incident_triggered
                and self.settings.claude_api_key
            ):
                await self._apply_claude_reasoning(
                    agents, positions, panic_levels, tick, total_ticks
                )

            # Record bottlenecks
            if tick % 30 == 0:
                bottleneck = self._detect_bottleneck(agents, positions)
                if bottleneck:
                    bottleneck_data.append({**bottleneck, "time_seconds": tick})

            # Sentiment trajectory (every 60 ticks)
            if tick % 60 == 0:
                avg_panic = float(np.mean(panic_levels))
                sentiment_trajectory.append(round(1.0 - avg_panic, 3))

            # Check if all evacuated
            evacuated_count = sum(1 for a in agents if a.evacuated)
            if evacuated_count >= len(agents) * 0.98 and all_evacuated_tick is None:
                all_evacuated_tick = tick
                break

        elapsed_ms = int((time.time() - t_start) * 1000)

        # Compute final stats
        final_evacuated = sum(1 for a in agents if a.evacuated)
        at_risk = sum(1 for a in agents if a.at_risk)
        delayed = len(agents) - final_evacuated - at_risk

        evac_time = (
            (all_evacuated_tick or total_ticks) - (evacuation_tick or 0)
        ) if evacuation_tick else total_ticks

        # Build result
        result = {
            "evacuation_time_seconds": evac_time,
            "evacuation_time_formatted": f"{evac_time // 60} min {evac_time % 60} sec",
            "target_met": evac_time <= 600,
            "bottlenecks": bottleneck_data[:5],
            "crowd_sentiment_trajectory": sentiment_trajectory,
            "peak_density": self._peak_density(positions),
            "estimated_injury_risk": round(min(1.0, at_risk / max(len(agents), 1)), 3),
            "agent_outcomes": {
                "safely_evacuated": final_evacuated,
                "delayed": max(0, delayed),
                "at_risk": at_risk,
            },
        }

        # Claude recommendations
        recs = await self.claude.produce_recommendations(
            result, event_cfg.model_dump()
        )
        result["recommendations"] = recs

        return {
            "simulation_id": sim_id,
            "scenario": self.request.scenario_id,
            "status": "completed",
            "duration_ms": elapsed_ms,
            "results": result,
        }

    def _trigger_incident(
        self,
        agents: list[Agent],
        positions: np.ndarray,
        panic_levels: np.ndarray,
        incident,
    ) -> None:
        """Set panic near incident location."""
        cx, cy = self.width / 2, self.height / 2  # default: center stage

        for i, agent in enumerate(agents):
            dist = np.sqrt((positions[i, 0] - cx) ** 2 + (positions[i, 1] - cy) ** 2)
            if dist < 20.0:  # 20m radius of incident
                initial_panic = max(0.6, 1.0 - dist / 20.0)
                # Non-compliant agents panic harder
                if agent.archetype.value == "non_compliant":
                    initial_panic = min(1.0, initial_panic * 1.3)
                panic_levels[i] = initial_panic
                agent.panic_level = initial_panic

    def _update_physics(
        self,
        agents: list[Agent],
        positions: np.ndarray,
        velocities: np.ndarray,
        panic_levels: np.ndarray,
        evacuation_started: bool,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Tick-based physics: move agents toward exits under panic pressure."""
        n = len(agents)

        for i, agent in enumerate(agents):
            if agent.evacuated:
                continue

            # Target: nearest exit if evacuating, else wander
            if evacuation_started and panic_levels[i] > 0.3:
                target = self._nearest_exit(positions[i])
                dx = target[0] - positions[i, 0]
                dy = target[1] - positions[i, 1]
                norm = max(np.sqrt(dx**2 + dy**2), 0.1)
                dx, dy = dx / norm, dy / norm
            else:
                dx = self.rng.uniform(-0.1, 0.1)
                dy = self.rng.uniform(-0.1, 0.1)

            speed = agent.profile.speed_with_modifier(agent.speed_modifier)
            speed *= 1.0 + panic_levels[i] * 0.5  # panic speeds movement

            velocities[i, 0] = dx * speed
            velocities[i, 1] = dy * speed

        positions = positions + velocities
        positions[:, 0] = np.clip(positions[:, 0], 0, self.width)
        positions[:, 1] = np.clip(positions[:, 1], 0, self.height)

        # Propagate panic from neighbors
        panic_spread = np.zeros(n)
        for i in range(n):
            if panic_levels[i] > 0.5:
                dists = np.sqrt(
                    (positions[:, 0] - positions[i, 0]) ** 2
                    + (positions[:, 1] - positions[i, 1]) ** 2
                )
                neighbors = np.where((dists < 5.0) & (dists > 0))[0]
                for j in neighbors:
                    influence = agents[i].profile.social_influence
                    panic_spread[j] += panic_levels[i] * influence * self.PANIC_SPREAD_RATE

        panic_levels = np.clip(panic_levels + panic_spread, 0.0, 1.0)

        return positions, velocities, panic_levels

    def _nearest_exit(self, pos: np.ndarray) -> tuple[float, float]:
        """Return coordinates of nearest exit."""
        min_dist = float("inf")
        nearest = self.exits[0]
        for ex, ey in self.exits:
            d = (pos[0] - ex) ** 2 + (pos[1] - ey) ** 2
            if d < min_dist:
                min_dist = d
                nearest = (ex, ey)
        return nearest

    def _mark_evacuated(self, agents: list[Agent], positions: np.ndarray) -> int:
        """Mark agents who've reached an exit as evacuated."""
        count = 0
        for i, agent in enumerate(agents):
            if agent.evacuated:
                continue
            for ex, ey in self.exits:
                if abs(positions[i, 0] - ex) < 2.0 and abs(positions[i, 1] - ey) < 2.0:
                    agent.evacuated = True
                    count += 1
                    break
        return count

    def _detect_bottleneck(
        self, agents: list[Agent], positions: np.ndarray
    ) -> Optional[dict]:
        """Find the exit with highest crowd pressure."""
        max_pressure = 0.0
        worst_exit = None

        for idx, (ex, ey) in enumerate(self.exits):
            nearby = np.sum(
                (np.abs(positions[:, 0] - ex) < 5.0) & (np.abs(positions[:, 1] - ey) < 5.0)
            )
            pressure = nearby / 25.0  # agents per 5m² grid cell
            if pressure > max_pressure:
                max_pressure = pressure
                worst_exit = f"exit_gate_{idx + 1}"

        if max_pressure > 4.0:
            return {"location": worst_exit, "peak_pressure": round(max_pressure, 1)}
        return None

    def _peak_density(self, positions: np.ndarray) -> float:
        """Compute peak local density (agents/m²) using a simple grid."""
        cell_size = 5.0
        cols = int(self.width / cell_size) + 1
        rows = int(self.height / cell_size) + 1
        grid = np.zeros((rows, cols))

        col_idx = (positions[:, 0] / cell_size).astype(int).clip(0, cols - 1)
        row_idx = (positions[:, 1] / cell_size).astype(int).clip(0, rows - 1)

        for c, r in zip(col_idx, row_idx):
            grid[r, c] += 1

        return round(float(grid.max()) / (cell_size ** 2), 2)

    async def _apply_claude_reasoning(
        self,
        agents: list[Agent],
        positions: np.ndarray,
        panic_levels: np.ndarray,
        tick: int,
        total_ticks: int,
    ) -> None:
        """Sample 10 agents and ask Claude to reason about their behavior."""
        n = len(agents)
        sample_indices = self.rng.choice(n, size=min(10, n), replace=False)

        agents_sample = []
        for i in sample_indices:
            agent = agents[i]
            agents_sample.append(
                {
                    "id": agent.id,
                    "archetype": agent.archetype.value,
                    "x": round(float(positions[i, 0]), 1),
                    "y": round(float(positions[i, 1]), 1),
                    "panic_level": round(float(panic_levels[i]), 2),
                }
            )

        event_ctx = {
            "venue": self.request.event_config.venue_name,
            "capacity": self.request.event_config.capacity,
            "incident": self.request.incident.type,
            "elapsed_seconds": tick,
            "total_seconds": total_ticks,
        }

        behaviors = await self.claude.generate_agent_behavior(agents_sample, event_ctx)

        # Apply returned behaviors to agents
        behavior_map = {b.get("agent_id"): b for b in (behaviors or [])}
        for i in sample_indices:
            behavior = behavior_map.get(agents[i].id)
            if behavior:
                agents[i].apply_behavior(
                    action=behavior.get("action", "hold"),
                    speed_modifier=float(behavior.get("speed_modifier", 1.0)),
                    panic_level=float(behavior.get("panic_level", panic_levels[i])),
                )
                panic_levels[i] = float(behavior.get("panic_level", panic_levels[i]))
