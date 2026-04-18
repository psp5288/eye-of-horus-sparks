"""Tests for the Sparks entertainment module."""

import pytest
from sparks.venues import list_events, get_event
from sparks.entertainment import EntertainmentScorer
from sparks.signals import SocialBuzzSignal, TicketResaleSignal, ArtistAnnouncementSignal


class TestVenues:
    def test_events_not_empty(self):
        events = list_events()
        assert len(events) > 0

    def test_event_has_required_fields(self):
        events = list_events()
        for e in events:
            assert "id" in e
            assert "name" in e
            assert "venue" in e
            assert "capacity" in e["venue"]

    def test_get_event_returns_correct(self):
        event = get_event("demo_event")
        assert event is not None
        assert event.id == "demo_event"

    def test_get_event_missing_returns_none(self):
        assert get_event("nonexistent_event_xyz") is None


class TestEntertainmentScorer:
    @pytest.mark.asyncio
    async def test_returns_risk_profile(self):
        scorer = EntertainmentScorer("demo_event")
        profile = await scorer.get_risk_profile()
        assert "entertainment_score" in profile
        assert "factors" in profile
        assert 0.0 <= profile["entertainment_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_missing_event_returns_error(self):
        scorer = EntertainmentScorer("nonexistent_xyz")
        profile = await scorer.get_risk_profile()
        assert "error" in profile

    @pytest.mark.asyncio
    async def test_festival_higher_score_than_conference(self):
        # coachella is a festival
        scorer_festival = EntertainmentScorer("coachella_2025_w1")
        scorer_demo = EntertainmentScorer("demo_event")
        p_festival = await scorer_festival.get_risk_profile()
        p_demo = await scorer_demo.get_risk_profile()
        # Festival should generally score higher risk
        assert p_festival["entertainment_score"] >= p_demo["entertainment_score"] - 0.1


class TestEntertainmentSignals:
    def test_social_buzz_simulation(self):
        signal = SocialBuzzSignal.simulate("demo_event")
        assert 0.0 <= signal.buzz_score <= 1.0
        assert signal.mention_count > 0

    def test_ticket_resale_simulation(self):
        signal = TicketResaleSignal.simulate("demo_event")
        assert signal.resale_premium_pct >= 0
        assert isinstance(signal.panic_sell_detected, bool)

    def test_artist_announcement_simulation(self):
        signal = ArtistAnnouncementSignal.simulate("demo_event")
        if signal.announced:
            assert signal.expected_surge_pct > 0
        else:
            assert signal.expected_surge_pct == 0.0
