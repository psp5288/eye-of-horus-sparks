"""Tests for the Oracle swarm simulation module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_swarm_initialization():
    """SwarmSimulation should initialize with correct agent count."""
    from oracle.swarm import SwarmSimulation
    sim = SwarmSimulation(num_agents=100, event_id="coachella_2023")
    sim.initialize_agents()
    assert len(sim.agents) > 0
    assert len(sim.agents) <= 100


def test_swarm_archetype_distribution():
    """Agents should be distributed across expected archetypes."""
    from oracle.swarm import SwarmSimulation
    from oracle.agents import AgentArchetype
    sim = SwarmSimulation(num_agents=1000, event_id="coachella_2023")
    sim.initialize_agents()

    archetypes = {a.archetype for a in sim.agents}
    assert AgentArchetype.CASUAL_ATTENDEE in archetypes
    assert AgentArchetype.STAFF in archetypes
    assert AgentArchetype.NON_COMPLIANT in archetypes


def test_agent_panic_level_valid():
    """All agents should have panic_level in [0, 1]."""
    from oracle.swarm import SwarmSimulation
    sim = SwarmSimulation(num_agents=200, event_id="astroworld_2024")
    sim.initialize_agents()
    for agent in sim.agents:
        assert 0.0 <= agent.panic_level <= 1.0, f"Agent {agent.id} panic_level out of range"


def test_scenario_parsing():
    """parse_scenario_input should return a valid Scenario."""
    from oracle.scenarios import parse_scenario_input
    scenario = parse_scenario_input({"incident_type": "crowd_surge", "severity": "high", "trigger_time_s": 1800})
    assert scenario.incident_type == "crowd_surge"
    assert scenario.severity == "high"
    assert scenario.trigger_time_s == 1800


def test_scenario_template():
    """SCENARIO_TEMPLATES should have expected keys."""
    from oracle.scenarios import SCENARIO_TEMPLATES
    assert "stage_rush" in SCENARIO_TEMPLATES
    assert "medical_cluster" in SCENARIO_TEMPLATES
    assert "controlled_evacuation" in SCENARIO_TEMPLATES


def test_scenario_defaults():
    """Empty input should return a valid default scenario."""
    from oracle.scenarios import parse_scenario_input
    scenario = parse_scenario_input({})
    assert scenario.incident_type is not None
    assert scenario.severity in ("low", "medium", "high")


@pytest.mark.asyncio
async def test_swarm_runs_and_returns_results():
    """run_simulation() should complete and return predictions dict."""
    from oracle.swarm import SwarmSimulation
    from oracle.scenarios import parse_scenario_input
    sim = SwarmSimulation(num_agents=200, event_id="super_bowl_58")
    scenario = parse_scenario_input({"incident_type": "evacuation", "severity": "low", "trigger_time_s": 30})
    results = await sim.run_simulation(scenario, num_ticks=50, use_claude=False)
    assert "predictions" in results
    assert "evacuation_time_seconds" in results["predictions"]
    assert results["predictions"]["evacuation_time_seconds"] > 0
