import { elements } from '../dom.js';

export function renderTimeline(report) {
  const items = report.dashboard?.timeline_items || [];
  const container = elements.ganttContainer();
  if (!items.length) {
    container.innerHTML = '<div class="empty-state"><p>No timeline data</p></div>';
    return;
  }

  const maxDays = Math.max(...items.map(i => i.lead_time_days || 14));
  const catColors = {
    powertrain: '#DC143C', braking_system: '#2196F3', body_chassis: '#4CAF50',
    electronics: '#FF9800', interior: '#9C27B0', suspension: '#00BCD4',
    wheels_tires: '#FFC107', exhaust_emissions: '#F44336',
  };

  container.innerHTML = items.map(item => {
    const days = item.lead_time_days || 14;
    const widthPct = (days / (maxDays + 5)) * 100;
    const color = catColors[item.category] || '#2196F3';
    const critical = item.critical_path ? 'critical' : '';
    return `
      <div class="gantt-row">
        <div class="gantt-label" title="${item.label}">${item.label}</div>
        <div class="gantt-bar-container">
          <div class="gantt-bar ${critical}" style="width:${widthPct}%;background:${color};left:0">${days}d</div>
        </div>
        <div class="gantt-days">${days} days</div>
      </div>
    `;
  }).join('');
}
