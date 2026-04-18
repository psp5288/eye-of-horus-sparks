"""Tests for the Oracle swarm simulation module."""

import pytest
import numpy as np
from oracle.agents import (
    Agent, AgentArchetype, ARCHETYPES, create_agent_population
)
from oracle.scenarios import SimulateRequest, get_built_in_scenarios


class TestAgentArchetypes:
    def test_all_archetypes_defined(self):
        for archetype in AgentArchetype:
            assert archetype in ARCHETYPES

    def test_staff_high_compliance(self):
        profile = ARCHETYPES[AgentArchetype.STAFF]
        assert profile.compliance == 1.0

    def test_non_compliant_low_compliance(self):
        profile = ARCHETYPES[AgentArchetype.NON_COMPLIANT]
        assert profile.compliance < 0.3

    def test_speed_clamped(self):
        profile = ARCHETYPES[AgentArchetype.CASUAL]
        assert profile.speed_with_modifier(10.0) <= 5.0
        assert profile.speed_with_modifier(0.0) == 0.0

    def test_panic_update_increases(self):
        agent = Agent(id=0, archetype=AgentArchetype.CASUAL, x=0, y=0)
        agent.update_panic(local_pressure=0.9)
        assert agent.panic_level > 0

    def test_panic_update_decreases_below_threshold(self):
        agent = Agent(id=0, archetype=AgentArchetype.CASUAL, x=0, y=0, panic_level=0.5)
        agent.update_panic(local_pressure=0.1)
        assert agent.panic_level < 0.5


class TestAgentPopulation:
    def setup_method(self):
        self.rng = np.random.default_rng(seed=0)

    def test_creates_correct_count(self):
        profile = {"casual": 0.5, "friends_group": 0.3, "staff": 0.2}
        agents = create_agent_population(100, profile, 200, 150, self.rng)
        # 100 * (0.5+0.3+0.2) = 100, but int rounding may give ±2
        assert 98 <= len(agents) <= 102

    def test_agents_within_bounds(self):
        profile = {"casual": 1.0}
        agents = create_agent_population(50, profile, 200, 150, self.rng)
        for a in agents:
            assert 0 <= a.x <= 200
            assert 0 <= a.y <= 150

    def test_agent_ids_unique(self):
        profile = {"casual": 0.5, "staff": 0.5}
        agents = create_agent_population(100, profile, 100, 100, self.rng)
        ids = [a.id for a in agents]
        assert len(ids) == len(set(ids))


class TestScenarios:
    def test_built_in_scenarios_not_empty(self):
        scenarios = get_built_in_scenarios()
        assert len(scenarios) >= 3

    def test_scenario_has_required_fields(self):
        for s in get_built_in_scenarios():
            assert "id" in s
            assert "name" in s
            assert "description" in s

    def test_simulate_request_defaults(self):
        req = SimulateRequest()
        assert req.simulation_config.agent_count == 10000
        assert req.simulation_config.duration_seconds == 600
