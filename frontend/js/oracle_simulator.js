/**
 * oracle_simulator.js — Oracle swarm simulation panel UI logic
 */

class OracleSimulator {
  constructor() {
    this._running = false;
  }

  init() {
    this._bindEvents();
  }

  _bindEvents() {
    const runBtn = document.getElementById('run-sim-btn');
    if (runBtn) runBtn.addEventListener('click', () => this.runSimulation());

    const suggestBtn = document.getElementById('suggest-scenarios-btn');
    if (suggestBtn) suggestBtn.addEventListener('click', () => this.suggestScenarios());
  }

  async runSimulation() {
    if (this._running) return;
    this._running = true;

    const runBtn = document.getElementById('run-sim-btn');
    if (runBtn) { runBtn.disabled = true; runBtn.textContent = 'Simulating…'; }

    const eventId  = document.getElementById('sim-event-select')?.value || 'coachella_2023';
    const type     = document.getElementById('incident-type')?.value || 'crowd_surge';
    const severity = document.getElementById('severity')?.value || 'medium';
    const triggerMin = parseInt(document.getElementById('trigger-time')?.value || '30', 10);

    const scenario = {
      incident_type: type,
      severity,
      trigger_time_s: triggerMin * 60,
    };

    const data = await EohAPI.runSimulation(eventId, scenario);

    if (runBtn) { runBtn.disabled = false; runBtn.textContent = 'Run Simulation'; }
    this._running = false;

    if (!data) {
      alert('Simulation failed — is the backend running on :8000?');
      return;
    }

    this._displayResults(data);
  }

  _displayResults(data) {
    const panel = document.getElementById('sim-results');
    if (!panel) return;
    panel.style.display = 'block';

    const preds = data.predictions || {};
    const outcomes = preds.agent_outcomes || {};

    this._setText('res-evac',     preds.evacuation_time_seconds || '--');
    this._setText('res-density',  preds.peak_density != null ? (preds.peak_density * 100).toFixed(1) + '%' : '--');
    this._setText('res-at-risk',  outcomes.at_risk ?? '--');
    this._setText('res-injured',  outcomes.injured ?? '--');

    this._renderBottlenecks(preds.bottlenecks || []);
    this._renderRecommendations(data.recommendations || []);
  }

  _renderBottlenecks(bottlenecks) {
    const el = document.getElementById('bottleneck-list');
    if (!el) return;
    if (!bottlenecks.length) {
      el.innerHTML = '<p style="color:var(--sev-nominal);font-size:13px;">No bottlenecks predicted.</p>';
      return;
    }
    el.innerHTML = '<h3 style="margin-bottom:8px;">Predicted Bottlenecks</h3>' +
      bottlenecks.map(b => `
        <div class="bottleneck-item">
          <span class="bn-location">${b.location}</span>
          <span class="bn-risk">Risk ${b.risk_score?.toFixed(1)}/10</span>
        </div>
      `).join('');
  }

  _renderRecommendations(recs) {
    const el = document.getElementById('recommendations-list');
    if (!el) return;
    if (!recs.length) return;
    el.innerHTML = '<h3 style="margin-bottom:8px;">Recommendations</h3>' +
      recs.map(r => `
        <div class="rec-item">
          <span class="rec-priority">#${r.priority}</span>
          <div class="rec-body">
            <div class="rec-action">${r.action}</div>
            <div class="rec-meta">${r.location} · ${r.timing} · ${r.expected_impact}</div>
          </div>
        </div>
      `).join('');
  }

  async suggestScenarios() {
    alert('Scenario suggestions require Claude API key — implement on April 21.');
  }

  _setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }
}

window.OracleSimulator = OracleSimulator;
