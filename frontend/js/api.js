/**
 * api.js — HTTP client for Eye of Horus: Sparks backend
 */

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : '';

const EohAPI = {
  async _fetch(path, opts = {}) {
    try {
      const res = await fetch(API_BASE + path, {
        headers: { 'Content-Type': 'application/json' },
        ...opts,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    } catch (err) {
      console.error('[EohAPI]', path, err);
      return null;
    }
  },

  /** GET /api/health */
  getHealthCheck() {
    return this._fetch('/api/health');
  },

  /** GET /api/iris/live-signals?event_id=... */
  getLiveSignals(eventId = 'coachella_2023') {
    return this._fetch(`/api/iris/live-signals?event_id=${eventId}`);
  },

  /** POST /api/oracle/simulate */
  runSimulation(eventId, scenario) {
    return this._fetch('/api/oracle/simulate', {
      method: 'POST',
      body: JSON.stringify({ event_id: eventId, scenario, num_agents: 10000, include_claude: true }),
    });
  },

  /** GET /api/sparks/events */
  getEvents() {
    return this._fetch('/api/sparks/events');
  },

  /** GET /api/sparks/events/:id */
  getEventProfile(eventId) {
    return this._fetch(`/api/sparks/events/${eventId}`);
  },

  /** GET /api/oracle/suggest?event_id=... */
  suggestScenarios(eventId = 'coachella_2023') {
    return this._fetch(`/api/oracle/suggest?event_id=${eventId}`);
  },

  /** GET /api/sparks/backtest */
  getBacktestResults() {
    return this._fetch('/api/sparks/backtest');
  },
};

window.EohAPI = EohAPI;
