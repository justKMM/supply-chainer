import { elements } from '../dom.js';

export function renderMetrics(report) {
  const grid = elements.metricsGrid();
  const metrics = report.dashboard?.hero_metrics || [];
  grid.innerHTML = metrics.map(m => `
    <div class="metric-card">
      <div class="metric-value">${m.value}</div>
      <div class="metric-label">${m.label}</div>
      ${m.trend ? `<div class="metric-trend ${m.trend}">\u2191 ${m.trend}</div>` : ''}
    </div>
  `).join('');
}
