import { elements } from '../dom.js';

export function renderIntelligence(report) {
  const signals = report.intelligence_feed || [];
  const container = elements.intelContainer();
  elements.intelCount().textContent = `${signals.length} signals`;

  container.innerHTML = signals.map(s => {
    const evt = s.event || {};
    const severity = evt.severity || 'medium';
    const actions = (evt.recommended_actions || []).slice(0, 3);
    return `
      <div class="intel-item">
        <div class="intel-header">
          <span class="intel-severity ${severity}">${severity}</span>
          <span class="sub-tag">${(evt.category || '').replace(/_/g, ' ')}</span>
          <span class="intel-source">${evt.source || ''}</span>
        </div>
        <div class="intel-title">${evt.title || ''}</div>
        <div class="intel-desc">${evt.description || ''}</div>
        ${actions.length ? `<div class="intel-actions">Recommended: ${actions.join(' | ')}</div>` : ''}
        <div class="intel-recipients">Delivered to ${s.recipient_count || 0} subscribed agents</div>
        ${s.ai_reaction ? `<div class="intel-reaction">Ferrari Procurement: "${s.ai_reaction}"</div>` : ''}
      </div>
    `;
  }).join('') || '<div class="empty-state"><p>No intelligence signals</p></div>';
}
