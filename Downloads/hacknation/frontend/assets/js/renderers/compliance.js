import { elements } from '../dom.js';

export function renderCompliance(report) {
  const comp = report.compliance_summary || {};
  const container = elements.complianceContainer();
  container.innerHTML = `
    <div class="compliance-grid">
      <div class="compliance-stat total"><div class="number">${comp.total_checks||0}</div><div class="label">Total Checks</div></div>
      <div class="compliance-stat pass"><div class="number">${comp.passed||0}</div><div class="label">Passed</div></div>
      <div class="compliance-stat flag"><div class="number">${comp.flagged||0}</div><div class="label">Flagged</div></div>
      <div class="compliance-stat fail"><div class="number">${comp.failed||0}</div><div class="label">Failed</div></div>
    </div>
    ${(comp.flags||[]).map(f => `
      <div class="risk-item">
        <span class="risk-badge medium">WARNING</span>
        <span class="risk-title">${f.agent_id}</span>
        <div class="risk-detail">${f.detail}</div>
      </div>
    `).join('')}
  `;
}
