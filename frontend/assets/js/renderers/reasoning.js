import { elements } from '../dom.js';

export function renderReasoning(report) {
  const log = report.reasoning_log || [];
  const container = elements.reasoningContainer();
  elements.reasoningCount().textContent = `${log.length} decisions`;

  container.innerHTML = log.map(r => `
    <div class="reasoning-item">
      <div class="reasoning-agent">
        <span style="color:${r.agent.includes('Ferrari') ? 'var(--ferrari-red)' : 'var(--accent-blue)'}">${r.agent}</span>
      </div>
      <div class="reasoning-thought">"${r.thought}"</div>
    </div>
  `).join('') || '<div class="empty-state"><p>No reasoning data</p></div>';
}
