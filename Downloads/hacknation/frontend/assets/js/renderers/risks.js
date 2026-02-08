import { elements } from '../dom.js';

export function renderRisks(report) {
  const risks = report.dashboard?.risk_items || report.execution_plan?.risk_assessment?.risks || [];
  const container = elements.riskContainer();
  const overall = report.execution_plan?.risk_assessment?.overall_risk || 'medium';
  elements.overallRisk().textContent = overall.toUpperCase();
  elements.overallRisk().className = `risk-badge ${overall}`;

  container.innerHTML = risks.map(r => `
    <div class="risk-item">
      <span class="risk-badge ${r.type === 'single_source_dependency' ? 'high' : 'low'}">${r.type === 'single_source_dependency' ? 'HIGH' : 'LOW'}</span>
      <span class="risk-title">${r.type?.replace(/_/g, ' ')}: ${r.component || ''}</span>
      <div class="risk-detail">${r.detail || r.supplier || ''}</div>
      <div class="risk-mitigation">\u2192 ${r.mitigation || ''}</div>
    </div>
  `).join('') || '<div class="empty-state"><p>No risks identified</p></div>';
}
