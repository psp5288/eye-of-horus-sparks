/**
 * iris_dashboard.js — Iris monitoring panel UI logic
 */

let _gaugeChart = null;

// Risk level → severity chip mapping
const RISK_TO_SEV = {
  LOW:      'nominal',
  MODERATE: 'watch',
  HIGH:     'elevated',
  CRITICAL: 'critical',
};

// Severity → signal bar color
const SEV_COLORS = {
  nominal:  'var(--sev-nominal)',
  watch:    'var(--sev-watch)',
  elevated: 'var(--sev-elevated)',
  critical: 'var(--sev-critical)',
};

const IrisDashboard = {
  async init(eventId) {
    this.eventId = eventId;
    this._initGauge();
    this._initSeverityMarks();
    await this.refresh();
    setInterval(() => this.refresh(), 30_000);

    document.getElementById('iris-refresh-btn').addEventListener('click', () => this.refresh());
    document.getElementById('interpret-btn').addEventListener('click', () => this.askClaude());
  },

  async refresh() {
    try {
      const status = await API.irisStatus(this.eventId);
      this._renderStatus(status);
    } catch (e) {
      console.error('Iris refresh failed:', e);
    }
  },

  _renderStatus(status) {
    const score = status.risk_score ?? 0;
    const level = status.risk_level ?? 'LOW';
    const conf  = status.confidence ?? 0;
    const sig   = status.signals ?? {};
    const sev   = RISK_TO_SEV[level] ?? 'nominal';

    this._updateGauge(score, sev);
    this._updateSeverityChips(sev);

    _setBar('twitter', sig.twitter_sentiment?.score ?? 0, sev);
    _setBar('weather', sig.weather?.score ?? 0, sev);
    _setBar('density', sig.crowd_density?.score ?? 0, sev);
    _setBar('velocity', sig.ticket_velocity?.score ?? 0, sev);

    document.getElementById('confidence-display').textContent = `${(conf * 100).toFixed(0)}%`;

    const alertBox = document.getElementById('iris-alert');
    if (status.alert) {
      alertBox.classList.remove('hidden');
      document.getElementById('iris-alert-text').textContent = status.alert;
    } else {
      alertBox.classList.add('hidden');
    }
  },

  _initGauge() {
    const ctx = document.getElementById('risk-gauge').getContext('2d');
    _gaugeChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [0, 100],
          backgroundColor: ['var(--sev-nominal)', 'rgba(255,255,255,0.06)'],
          borderWidth: 0,
          circumference: 180,
          rotation: 270,
        }],
      },
      options: {
        cutout: '78%',
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        animation: { duration: 600 },
      },
    });
  },

  _updateGauge(score, sev) {
    const pct = score * 100;
    const colorVar = SEV_COLORS[sev] || 'var(--sev-nominal)';

    // Chart.js can't read CSS vars directly — resolve via a temporary element
    const tmp = document.createElement('span');
    tmp.style.color = colorVar;
    document.body.appendChild(tmp);
    const color = getComputedStyle(tmp).color;
    document.body.removeChild(tmp);

    _gaugeChart.data.datasets[0].data = [pct, 100 - pct];
    _gaugeChart.data.datasets[0].backgroundColor[0] = color;
    _gaugeChart.update();

    const scoreEl = document.getElementById('risk-score-display');
    const levelEl = document.getElementById('risk-level-display');
    scoreEl.textContent = score.toFixed(2);
    levelEl.textContent = sev.toUpperCase();
    levelEl.style.color = colorVar;
  },

  /** Render the Wedjat glyph into each severity chip and mark the active one. */
  _initSeverityMarks() {
    ['sev-0', 'sev-1', 'sev-2', 'sev-3'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = wedjatSvg('glyph');
    });
  },

  _updateSeverityChips(activeSev) {
    document.querySelectorAll('.sev-chip').forEach(chip => {
      chip.classList.toggle('active', chip.dataset.sev === activeSev);
    });
  },

  async askClaude() {
    const btn = document.getElementById('interpret-btn');
    const output = document.getElementById('claude-interpret-output');
    btn.disabled = true;
    btn.textContent = 'Asking Claude…';

    try {
      const result = await API.irisInterpret(this.eventId);
      output.classList.remove('hidden');
      output.innerHTML = `
        <strong>Primary Risk:</strong> ${result.primary_risk ?? 'N/A'}<br><br>
        <strong>Alert:</strong> ${result.alert ?? 'No alert.'}<br><br>
        <em>${result.confidence_note ?? ''}</em>
      `;
    } catch (e) {
      output.classList.remove('hidden');
      output.textContent = `Claude unavailable: ${e.message}`;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Ask Claude to Interpret';
    }
  },
};

// ── Helpers ──────────────────────────────────────────────────

function _setBar(key, score, sev) {
  const bar = document.getElementById(`bar-${key}`);
  const val = document.getElementById(`val-${key}`);
  if (!bar || !val) return;

  const pct = (score * 100).toFixed(0);
  bar.style.width = `${pct}%`;
  val.textContent = `${pct}%`;

  // Bar colour tracks the per-signal risk, not the composite
  if (score < 0.3) {
    bar.style.background = 'var(--sev-nominal)';
  } else if (score < 0.6) {
    bar.style.background = 'var(--sev-watch)';
  } else if (score < 0.8) {
    bar.style.background = 'var(--sev-elevated)';
  } else {
    bar.style.background = 'var(--sev-critical)';
  }
}
