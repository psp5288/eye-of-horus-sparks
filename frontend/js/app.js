/**
 * app.js — Main application entry point
 */

document.addEventListener('DOMContentLoaded', () => {
  // ── Logo ───────────────────────────────────────────
  const logoEl = document.getElementById('header-logo');
  if (logoEl && window.WedjatLogo) {
    const logo = new WedjatLogo(logoEl, 'hover');
    logo.init('wedjat');
  }

  // ── Health check ───────────────────────────────────
  (async () => {
    const dot   = document.getElementById('api-status-dot');
    const label = document.getElementById('api-status-label');
    const data  = await EohAPI.getHealthCheck();
    if (data?.status === 'ok') {
      if (dot)   { dot.classList.add('online'); }
      if (label) { label.textContent = 'API Online'; }
    } else {
      if (dot)   { dot.classList.add('offline'); }
      if (label) { label.textContent = 'API Offline'; }
    }
  })();

  // ── Navigation ─────────────────────────────────────
  const navBtns = document.querySelectorAll('.nav-btn');
  const views   = document.querySelectorAll('.view');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.view;
      navBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      views.forEach(v => v.classList.toggle('active', v.id === `view-${target}`));
      if (target === 'about') loadBacktest();
    });
  });

  // ── Module init ────────────────────────────────────
  const iris = new IrisDashboard();
  iris.init();

  const oracle = new OracleSimulator();
  oracle.init();

  // ── Backtest table (About view) ────────────────────
  async function loadBacktest() {
    const el = document.getElementById('backtest-table');
    if (!el || el.dataset.loaded) return;
    const data = await EohAPI.getBacktestResults();
    if (!data) {
      el.textContent = 'Backtest data unavailable.';
      return;
    }
    el.innerHTML = `
      <table>
        <thead><tr>
          <th>Event</th><th>Risk Level Correct</th>
          <th>Evac Error</th><th>Accuracy</th>
        </tr></thead>
        <tbody>
          ${data.events.map(e => `
            <tr>
              <td>${e.event_id.replace(/_/g,' ')}</td>
              <td>${e.risk_level_correct ? '✓' : '✗'}</td>
              <td>${e.evacuation_time_error_pct}%</td>
              <td class="acc">${(e.accuracy * 100).toFixed(1)}%</td>
            </tr>
          `).join('')}
          <tr style="border-top:2px solid var(--border-color)">
            <td><strong>Overall</strong></td>
            <td></td><td></td>
            <td class="acc"><strong>${(data.overall_accuracy * 100).toFixed(1)}%</strong></td>
          </tr>
        </tbody>
      </table>
    `;
    el.dataset.loaded = '1';
  }
});
