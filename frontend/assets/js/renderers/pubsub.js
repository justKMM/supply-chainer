import { elements } from '../dom.js';

export function renderPubSub(report) {
  const summary = report.pubsub_summary || {};
  const subs = summary.subscriptions || [];
  const container = elements.pubsubContainer();
  elements.subCount().textContent = `${subs.length} agents`;

  let html = `
    <div class="sub-stat" style="padding:12px 16px;border-bottom:1px solid var(--border);">
      <div class="sub-stat-item"><div class="num">${summary.total_events || 0}</div><div class="lbl">Events</div></div>
      <div class="sub-stat-item"><div class="num">${summary.total_subscriptions || 0}</div><div class="lbl">Subscribers</div></div>
      <div class="sub-stat-item"><div class="num">${summary.total_deliveries || 0}</div><div class="lbl">Deliveries</div></div>
    </div>
  `;

  html += subs.map(s => `
    <div class="sub-item">
      <div class="sub-agent">${s.agent_name || s.agent_id}</div>
      <div class="sub-categories">
        ${(s.categories || []).map(c => `<span class="sub-tag">${c.replace(/_/g, ' ')}</span>`).join('')}
      </div>
    </div>
  `).join('');

  container.innerHTML = html || '<div class="empty-state"><p>No subscriptions</p></div>';
}
