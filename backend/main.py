"""FastAPI entry point for Eye of Horus: Sparks."""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings

settings = get_settings()

app = FastAPI(
    title="Eye of Horus: Sparks",
    description="AI-powered crowd intelligence for live events",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "1.0.0",
        "vertical": settings.vertical,
        "claude_configured": bool(settings.claude_api_key),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Iris routes ───────────────────────────────────────────────────────────

@app.get("/api/iris/live-signals")
async def get_live_signals(event_id: str = "coachella_2023"):
    from iris.monitor import IrisMonitor
    monitor = IrisMonitor()
    signals = await monitor.fetch_signals(event_id)
    return signals


# ── Oracle routes ─────────────────────────────────────────────────────────

@app.post("/api/oracle/simulate")
async def run_simulation(body: dict):
    from oracle.swarm import SwarmSimulation
    from oracle.scenarios import parse_scenario_input

    event_id = body.get("event_id", "coachella_2023")
    scenario_data = body.get("scenario", {})
    num_agents = body.get("num_agents", 10000)
    include_claude = body.get("include_claude", True)

    scenario = parse_scenario_input(scenario_data)
    sim = SwarmSimulation(num_agents=num_agents, event_id=event_id)
    results = await sim.run_simulation(scenario, use_claude=include_claude)
    return results


# ── Sparks routes ─────────────────────────────────────────────────────────

@app.get("/api/sparks/events")
async def list_events():
    from sparks.venues import list_all_events
    return list_all_events()


@app.get("/api/sparks/events/{event_id}")
async def get_event_risk_profile(event_id: str):
    from sparks.entertainment import EntertainmentScorer
    scorer = EntertainmentScorer(event_id)
    profile = await scorer.get_risk_profile()
    if "error" in profile:
        raise HTTPException(status_code=404, detail=profile["error"])
    return profile


@app.get("/api/sparks/backtest")
async def get_backtest_results():
    import json
    from pathlib import Path
    data_file = Path(__file__).resolve().parents[1] / "data" / "backtest_events_complete.json"
    if not data_file.exists():
        raise HTTPException(status_code=404, detail="Backtest data not found")
    with open(data_file) as f:
        data = json.load(f)
    return {
        "overall_accuracy": data["metadata"]["accuracy_summary"]["overall_accuracy"],
        "target": data["metadata"]["accuracy_summary"]["accuracy_target"],
        "target_met": data["metadata"]["accuracy_summary"]["target_met"],
        "events": [
            {
                "event_id": e["event_id"],
                "risk_level_correct": data["metadata"]["accuracy_summary"][e["event_id"]]["risk_level_correct"],
                "evacuation_time_error_pct": data["metadata"]["accuracy_summary"][e["event_id"]]["evacuation_time_error_pct"],
                "accuracy": data["metadata"]["accuracy_summary"][e["event_id"]]["accuracy"],
            }
            for e in data["events"]
        ],
    }


# ── Vercel / Mangum adapter ───────────────────────────────────────────────

try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    pass
