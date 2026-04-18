/**
 * oracle_simulator.js — Oracle swarm simulation panel UI logic
 */

let _sentimentChart = null;

const OracleSimulator = {
  /**
   * Initialize the Oracle panel.
   */
  init() {
    this._initSentimentChart();
    this._bindControls();
  },

  _bindControls() {
    // Agent count slider label
    const slider = document.getElementById('agent-count');
    const display = document.getElementById('agent-count-display');
    slider.addEventListener('input', () => {
      display.textContent = Number(slider.value).toLocaleString();
    });

    // Run simulation button
    document.getElementById('run-sim-btn').addEventListener('click', () => this.runSimulation());

    // Suggest scenarios button
    document.getElementById('suggest-btn').addEventListener('click', () => this.suggestScenarios());
  },

  async runSimulation() {
    const btn = document.getElementById('run-sim-btn');
    btn.disabled = true;
    _showLoading('Running 10,000 agent simulation...');

    const payload = {
      scenario_id: document.getElementById('scenario-select').value,
      event_config: {
        venue_name: 'Hackathon Demo Venue',
        capacity: 20000,
        current_attendance: 18000,
        crowd_profile: {
          casual: 0.40,
          friends_group: 0.30,
          influencer: 0.10,
          staff: 0.15,
          non_compliant: 0.05,
        },
      },
      incident: {
        type: document.getElementById('incident-select').value,
        location: 'main_stage_pit',
        trigger_time_seconds: 180,
        severity: 'high',
      },
      simulation_config: {
        agent_count: Number(document.getElementById('agent-count').value),
        duration_seconds: 600,
        use_claude_reasoning: document.getElementById('use-claude').checked,
      },
    };

    try {
      const result = await API.oracleSimulate(payload);
      this._renderResult(result);
    } catch (e) {
      alert(`Simulation failed: ${e.message}`);
    } finally {
      btn.disabled = false;
      _hideLoading();
    }
  },

  _renderResult(data) {
    const r = data.results ?? {};
    document.getElementById('sim-results').classList.remove('hidden');

    document.getElementById('evac-time').textContent = r.evacuation_time_formatted ?? '--';
    document.getElementById('peak-density').textContent = r.peak_density ?? '--';
    document.getElementById('injury-risk').textContent =
      r.estimated_injury_risk != null ? `${(r.estimated_injury_risk * 100).toFixed(1)}%` : '--';
    document.getElementById('evacuated-count').textContent =
      (r.agent_outcomes?.safely_evacuated ?? '--').toLocaleString();

    // Sentiment chart
    this._updateSentimentChart(r.crowd_sentiment_trajectory ?? []);

    // Recommendations
    const recsList = document.getElementById('recs-list');
    recsList.innerHTML = '';
    for (const rec of (r.recommendations ?? [])) {
      const li = document.createElement('li');
      li.innerHTML = `<strong>#${rec.priority}</strong> ${rec.action}
        <span style="color:var(--text-muted)"> — ${rec.location ?? ''} ${rec.timing ? `(${rec.timing})` : ''}</span>`;
      recsList.appendChild(li);
    }

    // Bottlenecks
    const bnList = document.getElementById('bottleneck-list');
    bnList.innerHTML = '';
    for (const bn of (r.bottlenecks ?? [])) {
      const li = document.createElement('li');
      li.textContent = `${bn.location} — pressure ${bn.peak_pressure} agents/m² at T+${bn.time_seconds}s`;
      bnList.appendChild(li);
    }
  },

  _initSentimentChart() {
    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    _sentimentChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Crowd Sentiment',
          data: [],
          borderColor: '#7b5ea7',
          backgroundColor: 'rgba(123,94,167,0.15)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#6e6e8a' }, grid: { color: '#1a1a2e' } },
          y: {
            min: 0, max: 1,
            ticks: { color: '#6e6e8a' },
            grid: { color: '#1a1a2e' },
          },
        },
      },
    });
  },

  _updateSentimentChart(trajectory) {
    if (!trajectory.length) return;
    _sentimentChart.data.labels = trajectory.map((_, i) => `T+${i * 60}s`);
    _sentimentChart.data.datasets[0].data = trajectory;
    _sentimentChart.update();
  },

  async suggestScenarios() {
    const btn = document.getElementById('suggest-btn');
    const output = document.getElementById('scenario-suggestions');
    btn.disabled = true;
    btn.textContent = '𓂀 Asking Claude...';

    const eventConfig = {
      venue_name: 'Demo Venue',
      capacity: 20000,
      event_type: document.getElementById('scenario-select').value,
    };

    try {
      const result = await API.oracleSuggestScenarios(eventConfig);
      const scenarios = result.scenarios ?? [];
      output.classList.remove('hidden');
      output.innerHTML = scenarios.map(s =>
        `<div style="margin-bottom:12px">
          <strong style="color:var(--accent)">${s.name}</strong>
          <span style="margin-left:8px;color:var(--text-muted);font-size:11px;text-transform:uppercase">${s.severity}</span><br>
          <span>${s.description}</span>
        </div>`
      ).join('<hr style="border-color:var(--border);margin:8px 0">') || 'No suggestions returned.';
    } catch (e) {
      output.classList.remove('hidden');
      output.textContent = `Claude unavailable: ${e.message}`;
    } finally {
      btn.disabled = false;
      btn.textContent = '𓂀 Suggest Scenarios (Claude)';
    }
  },
};

// ── Helpers ──────────────────────────────────────────────────

function _showLoading(text) {
  document.getElementById('loading-text').textContent = text;
  document.getElementById('loading-overlay').classList.remove('hidden');
}

function _hideLoading() {
  document.getElementById('loading-overlay').classList.add('hidden');
}
