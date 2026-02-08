import { elements } from '../dom.js';

export function renderReputation(report) {
  const rep = report.reputation_summary || {};
  const leaderboard = rep.leaderboard || [];
  const chains = rep.chain_verifications || {};
  const container = elements.reputationContainer();
  elements.reputationCount().textContent =
    `${rep.total_agents_scored || 0} agents | ${rep.total_attestations || 0} attestations`;

  if (!leaderboard.length) {
    container.innerHTML = '<div class="empty-state"><p>No reputation data</p></div>';
    return;
  }

  const trendSymbols = { improving: '\u2191', stable: '\u2192', declining: '\u2193' };

  container.innerHTML = `
    <table class="reputation-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Agent</th>
          <th>Composite</th>
          <th>Delivery</th>
          <th>Quality</th>
          <th>Pricing</th>
          <th>Compliance</th>
          <th>Reliability</th>
          <th>Txns</th>
          <th>Trend</th>
          <th>Chain</th>
        </tr>
      </thead>
      <tbody>
        ${leaderboard.map((r, i) => {
          const chain = chains[r.agent_id] || {};
          const composite_pct = (r.composite_score * 100).toFixed(1);
          const barColor = r.composite_score > 0.85 ? '#4CAF50' :
                           r.composite_score > 0.65 ? '#FF9800' : '#F44336';
          return `
            <tr>
              <td style="color:var(--text-muted)">${i + 1}</td>
              <td><span style="font-weight:600">${r.agent_name || r.agent_id}</span></td>
              <td>
                <span class="score-bar" style="width:${composite_pct * 0.6}px;background:${barColor}"></span>
                <span class="score-value" style="color:${barColor}">${composite_pct}%</span>
              </td>
              <td style="color:${r.delivery > 0.8 ? '#4CAF50' : '#FF9800'}">${(r.delivery * 100).toFixed(0)}%</td>
              <td style="color:${r.quality > 0.8 ? '#4CAF50' : '#FF9800'}">${(r.quality * 100).toFixed(0)}%</td>
              <td style="color:${r.pricing > 0.8 ? '#4CAF50' : '#FF9800'}">${(r.pricing * 100).toFixed(0)}%</td>
              <td style="color:${r.compliance > 0.8 ? '#4CAF50' : '#FF9800'}">${(r.compliance * 100).toFixed(0)}%</td>
              <td style="color:${r.reliability > 0.8 ? '#4CAF50' : '#FF9800'}">${(r.reliability * 100).toFixed(0)}%</td>
              <td style="color:var(--text-muted)">${r.transactions}</td>
              <td><span class="trend-indicator ${r.trend}">${trendSymbols[r.trend] || '-'} ${r.trend}</span></td>
              <td><span class="chain-badge ${chain.valid ? 'valid' : 'invalid'}">${chain.valid ? 'Verified' : 'Invalid'} (${chain.length || 0})</span></td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;
}
