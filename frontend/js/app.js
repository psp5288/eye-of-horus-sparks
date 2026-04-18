/**
 * app.js — Main application entry point
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize header animated logo (hover-to-reveal "Horus")
  const headerLogoEl = document.getElementById('header-logo');
  if (headerLogoEl && window.WedjatLogo) {
    const headerLogo = new WedjatLogo(headerLogoEl, 'hover');
    headerLogo.init('wedjat');
  }

  // Verify backend connectivity
  try {
    await API.health();
    console.log('Backend connected ✓');
  } catch (e) {
    console.warn('Backend not reachable — running in demo mode:', e.message);
  }

  // Load events and set active event name in header
  const activeEventId = await _loadActiveEvent();

  // Initialize panels
  IrisDashboard.init(activeEventId);
  OracleSimulator.init();
});

async function _loadActiveEvent() {
  try {
    const data = await API.sparksEvents();
    const events = data.events ?? [];
    const active = events.find(e => e.status === 'active') ?? events[0];

    if (active) {
      document.getElementById('active-event-name').textContent = active.name;
      return active.id;
    }
  } catch (e) {
    console.warn('Could not load events:', e.message);
  }

  document.getElementById('active-event-name').textContent = 'Demo Event';
  return 'demo_event';
}
