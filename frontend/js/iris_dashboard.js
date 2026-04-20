/**
 * iris_dashboard.js — Real-time signal monitoring dashboard
 */

class IrisDashboard {
  constructor() {
    this._interval = null;
    this._currentEvent = 'coachella_2023';
  }

  init() {
    this._initSeverityMarks();
    this._bindEvents();
    this.refresh();
    this._startPolling();
  }

  _initSeverityMarks() {
    ['sev-0','sev-1','sev-2','sev-3'].forEach(id => {
      const el = document.getElementById(id);
      if (el && window.wedjatSvg) {
        el.insertAdjacentHTML('afterbegin', window.wedjatSvg('glyph', { size: 14 }) + ' ');
      }
    });
  }

  _bindEvents() {
    const sel = document.getElementById('event-select');
    if (sel) sel.addEventListener('change', e => {
      this._currentEvent = e.target.value;
      this.refresh();
    });
    const btn = document.getElementById('refresh-signals-btn');
    if (btn) btn.addEventListener('click', () => this.refresh());
  }

  async refresh() {
    const data = await EohAPI.getLiveSignals(this._currentEvent);
    if (!data) return;
    this._updateKPIs(data);
    this._updateSignalBars(data);
    this._updateSeverityChips(data.risk_level);
    this._updateAlert(data.claude_interpretation);
    this._updateTimestamp();
  }

  _updateTimestamp() {
    const el = document.getElementById('iris-last-updated');
    if (el) el.textContent = 'Last updated: ' + new Date().toLocaleTimeString();
  }

  _updateKPIs(data) {
    const scores = data.scores || {};
    const map = {
      'kpi-safety': 'Safety',
      'kpi-revenue': 'Revenue',
      'kpi-experience': 'Experience',
      'kpi-bottleneck': 'Bottleneck',
    };
    for (const [id, key] of Object.entries(map)) {
      const el = document.querySelector(`#${id} .score-value`);
      if (el) el.textContent = scores[key] !== undefined ? scores[key] : '--';
    }
  }

  _updateSignalBars(data) {
    const signals = data.signals || {};
    const rows = [
      { id: 'sig-twitter', value: signals.twitter?.sentiment_score,        invert: true },
      { id: 'sig-weather', value: signals.weather?.risk_score,              invert: false },
      { id: 'sig-density', value: signals.crowd_density?.density_score,     invert: false },
      { id: 'sig-ticket',  value: signals.ticket_velocity?.velocity_score,  invert: false },
    ];
    rows.forEach(({ id, value, invert }) => {
      if (value == null) return;
      const row = document.getElementById(id);
      if (!row) return;
      const risk = invert ? (1 - value) : value;
      const fill = row.querySelector('.signal-bar-fill');
      const label = row.querySelector('.signal-value');
      if (fill) {
        fill.style.width = `${Math.round(risk * 100)}%`;
        fill.style.background = this._riskColor(risk);
      }
      if (label) label.textContent = risk.toFixed(2);
    });
  }

  _riskColor(score) {
    if (score < 0.3) return 'var(--sev-nominal)';
    if (score < 0.6) return 'var(--sev-watch)';
    if (score < 0.8) return 'var(--sev-elevated)';
    return 'var(--sev-critical)';
  }

  _updateSeverityChips(level) {
    const map = { LOW: 'nominal', MODERATE: 'watch', HIGH: 'elevated', CRITICAL: 'critical' };
    const active = map[level] || 'nominal';
    ['nominal','watch','elevated','critical'].forEach(sev => {
      document.querySelectorAll(`[data-sev="${sev}"]`)
        .forEach(c => c.classList.toggle('active', sev === active));
    });
  }

  _updateAlert(interp) {
    const box = document.getElementById('claude-alert-box');
    if (!box || !interp?.alert) return;
    box.textContent = interp.alert;
    box.style.display = 'block';
  }

  _startPolling() {
    this._interval = setInterval(() => this.refresh(), 5000);
  }

  destroy() { clearInterval(this._interval); }
}

window.IrisDashboard = IrisDashboard;
