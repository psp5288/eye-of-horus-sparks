/**
 * api.js — HTTP client for Eye of Horus: Sparks backend
 *
 * Change API_BASE_URL to your Vercel deployment URL in production.
 */

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : '';  // same origin on Vercel

const API = {
  /** GET /api/health */
  async health() {
    return _get('/api/health');
  },

  /** GET /api/iris/status?event_id=... */
  async irisStatus(eventId = 'demo_event') {
    return _get(`/api/iris/status?event_id=${encodeURIComponent(eventId)}`);
  },

  /** POST /api/iris/interpret */
  async irisInterpret(eventId = 'demo_event') {
    return _post('/api/iris/interpret', { event_id: eventId });
  },

  /** GET /api/oracle/scenarios */
  async oracleScenarios() {
    return _get('/api/oracle/scenarios');
  },

  /** POST /api/oracle/simulate */
  async oracleSimulate(payload) {
    return _post('/api/oracle/simulate', payload);
  },

  /** POST /api/oracle/suggest-scenarios */
  async oracleSuggestScenarios(eventConfig) {
    return _post('/api/oracle/suggest-scenarios', { event_config: eventConfig });
  },

  /** GET /api/sparks/events */
  async sparksEvents() {
    return _get('/api/sparks/events');
  },

  /** GET /api/sparks/events/:id/risk-profile */
  async sparksRiskProfile(eventId) {
    return _get(`/api/sparks/events/${encodeURIComponent(eventId)}/risk-profile`);
  },

  /** POST /api/backtest/run */
  async backtestRun(eventIds, simulationConfig = {}) {
    return _post('/api/backtest/run', { event_ids: eventIds, simulation_config: simulationConfig });
  },
};

// ── Internal helpers ──────────────────────────────────────────

async function _get(path) {
  const res = await fetch(API_BASE_URL + path);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message || `HTTP ${res.status}`);
  }
  return res.json();
}

async function _post(path, body) {
  const res = await fetch(API_BASE_URL + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message || `HTTP ${res.status}`);
  }
  return res.json();
}
