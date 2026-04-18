"""FastAPI entry point for Eye of Horus: Sparks."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from config import get_settings
from iris.monitor import IrisMonitor
from oracle.swarm import SwarmSimulation
from oracle.scenarios import get_built_in_scenarios
from oracle.claude_integration import ClaudeIntegration
from sparks.venues import list_events
from iris.models import IrisStatusResponse, SignalFeedResponse
from oracle.scenarios import SimulateRequest
from sparks.entertainment import EntertainmentScorer

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered crowd intelligence for live events",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
_frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(_frontend_path):
    app.mount("/static", StaticFiles(directory=_frontend_path), name="static")


# ──────────────────────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Service health check."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "modules": {
            "iris": "operational",
            "oracle": "operational",
            "sparks": "operational",
        },
    }


# ──────────────────────────────────────────────────────────────
# Iris — Real-Time Monitoring
# ──────────────────────────────────────────────────────────────

@app.get("/api/iris/status")
async def iris_status(event_id: str = "demo_event"):
    """Return current composite risk score and signal breakdown."""
    monitor = IrisMonitor(event_id=event_id)
    status = await monitor.get_status()
    return status


@app.get("/api/iris/signals")
async def iris_signals(event_id: str = "demo_event", minutes: int = 60):
    """Return raw signal feed for the last N minutes."""
    monitor = IrisMonitor(event_id=event_id)
    feed = await monitor.get_signal_feed(window_minutes=minutes)
    return feed


@app.post("/api/iris/interpret")
async def iris_interpret(body: dict):
    """Ask Claude to interpret current signals and produce a natural language alert."""
    event_id = body.get("event_id", "demo_event")
    monitor = IrisMonitor(event_id=event_id)
    status = await monitor.get_status()
    claude = ClaudeIntegration()
    result = await claude.interpret_signals(status.signals, status.risk_score)
    return result


# ──────────────────────────────────────────────────────────────
# Oracle — Swarm Simulation
# ──────────────────────────────────────────────────────────────

@app.get("/api/oracle/scenarios")
async def oracle_scenarios():
    """Return list of available simulation scenarios."""
    return {"built_in": get_built_in_scenarios(), "saved": []}


@app.post("/api/oracle/simulate")
async def oracle_simulate(request: SimulateRequest):
    """Run a swarm simulation for a given scenario and event config."""
    simulation = SwarmSimulation(request=request, settings=settings)
    result = await simulation.run()
    return result


@app.post("/api/oracle/suggest-scenarios")
async def oracle_suggest_scenarios(body: dict):
    """Ask Claude to generate what-if scenarios for an event."""
    claude = ClaudeIntegration()
    scenarios = await claude.generate_scenarios(event_config=body.get("event_config", {}))
    return {"scenarios": scenarios}


# ──────────────────────────────────────────────────────────────
# Sparks — Entertainment Events
# ──────────────────────────────────────────────────────────────

@app.get("/api/sparks/events")
async def sparks_events():
    """Return list of configured events."""
    return {"events": list_events()}


@app.get("/api/sparks/events/{event_id}/risk-profile")
async def sparks_risk_profile(event_id: str):
    """Return entertainment-specific risk profile for an event."""
    scorer = EntertainmentScorer(event_id=event_id)
    return await scorer.get_risk_profile()


# ──────────────────────────────────────────────────────────────
# Backtesting
# ──────────────────────────────────────────────────────────────

@app.post("/api/backtest/run")
async def backtest_run(body: dict):
    """Run backtesting against historical event data."""
    from oracle.scenarios import run_backtest
    results = await run_backtest(
        event_ids=body.get("event_ids", []),
        simulation_config=body.get("simulation_config", {}),
    )
    return results


# ──────────────────────────────────────────────────────────────
# Frontend catchall
# ──────────────────────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    """Serve the frontend dashboard."""
    index_path = os.path.join(_frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Eye of Horus: Sparks API", "docs": "/docs"}


# Vercel / Mangum adapter
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    pass
