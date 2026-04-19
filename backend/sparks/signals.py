"""Entertainment-specific signal definitions for the Sparks vertical."""

import random
from typing import Any

ENTERTAINMENT_SIGNALS: dict[str, dict[str, Any]] = {
    "twitter_sentiment": {
        "source": "Twitter API v2",
        "keywords": ["concert", "festival", "venue", "crowd", "stage", "crush", "push", "emergency"],
        "confidence_weight": 0.60,
        "freshness": "real-time",
        "affects": ["overall_sentiment", "panic_risk"],
        "invert": True,
        "description": "Negative tweets are a leading indicator of crowd distress (precede physical incidents by ~20 min)",
    },
    "weather": {
        "source": "OpenWeatherMap API",
        "keywords": [],
        "confidence_weight": 0.45,
        "freshness": "10-minute intervals",
        "affects": ["medical_risk", "crowd_behavior"],
        "invert": False,
        "description": "High temperature + humidity increases medical incident probability",
    },
    "crowd_density": {
        "source": "Venue sensors / check-in data",
        "keywords": [],
        "confidence_weight": 0.80,
        "freshness": "1-minute intervals",
        "affects": ["bottleneck_risk", "evacuation_time", "injury_risk"],
        "invert": False,
        "description": "Primary physical risk driver. Critical threshold: 4.5 persons/sqm",
    },
    "ticket_velocity": {
        "source": "Ticketmaster API + resale market",
        "keywords": [],
        "confidence_weight": 0.35,
        "freshness": "hourly",
        "affects": ["expected_attendance", "non_compliance_estimate"],
        "invert": False,
        "description": "Resale spikes indicate demand overflow — proxy for crowd beyond capacity",
    },
    "social_checkins": {
        "source": "Instagram / TikTok geotags",
        "keywords": ["concert", "festival", "venue", "live"],
        "confidence_weight": 0.25,
        "freshness": "15-minute intervals",
        "affects": ["attendance_estimate", "zone_density"],
        "invert": False,
        "description": "Social check-ins provide crowd distribution heatmap proxy",
    },
    "artist_sentiment": {
        "source": "Twitter mentions of headliner",
        "keywords": [],
        "confidence_weight": 0.30,
        "freshness": "real-time",
        "affects": ["crowd_energy", "stage_rush_probability"],
        "invert": False,
        "description": "High artist hype correlates with crowd surge probability near stage",
    },
    "wait_times": {
        "source": "Venue app / staff reports",
        "keywords": ["wait", "line", "queue"],
        "confidence_weight": 0.40,
        "freshness": "5-minute intervals",
        "affects": ["bottleneck_locations", "exit_congestion"],
        "invert": False,
        "description": "Long entry/exit queues indicate bottleneck formation",
    },
}


def get_signal_mock(signal_name: str, event_id: str) -> float:
    """
    Return a mock signal score for dev/demo mode.

    Parameters
    ----------
    signal_name : str
        Key from ENTERTAINMENT_SIGNALS.
    event_id : str
        Event identifier for context-appropriate mocks.

    Returns
    -------
    float
        Score 0–1.
    """
    _MOCKS = {
        "astroworld_2024": {
            "twitter_sentiment": 0.78, "weather": 0.05, "crowd_density": 0.87,
            "ticket_velocity": 0.85, "social_checkins": 0.70, "artist_sentiment": 0.90, "wait_times": 0.60,
        },
        "coachella_2023": {
            "twitter_sentiment": 0.35, "weather": 0.18, "crowd_density": 0.72,
            "ticket_velocity": 0.55, "social_checkins": 0.65, "artist_sentiment": 0.75, "wait_times": 0.45,
        },
        "super_bowl_58": {
            "twitter_sentiment": 0.20, "weather": 0.08, "crowd_density": 0.55,
            "ticket_velocity": 0.40, "social_checkins": 0.50, "artist_sentiment": 0.60, "wait_times": 0.25,
        },
    }
    event_mocks = _MOCKS.get(event_id, {})
    return event_mocks.get(signal_name, random.uniform(0.3, 0.7))
