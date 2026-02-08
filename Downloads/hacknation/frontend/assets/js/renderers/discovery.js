import { elements } from '../dom.js';

export function renderDiscovery(report) {
  const paths = report.discovery_results?.discovery_paths || [];
  const container = elements.discoveryContainer();

  container.innerHTML = `
    <div style="padding:10px 16px;border-bottom:1px solid rgba(42,42,68,0.5);font-size:12px;">
      <span style="color:var(--accent-blue);font-weight:600">${report.discovery_results?.agents_discovered||0}</span> discovered &bull;
      <span style="color:var(--accent-green);font-weight:600">${report.discovery_results?.agents_qualified||0}</span> qualified &bull;
      <span style="color:#F44336;font-weight:600">${report.discovery_results?.agents_disqualified||0}</span> disqualified
    </div>
  ` + paths.map(p => `
    <div class="discovery-item">
      <div class="discovery-need">${p.need}</div>
      <div class="discovery-query">${p.query}</div>
      <div class="discovery-result">\u2192 ${p.selected} (${p.results_count} candidates)</div>
    </div>
  `).join('');
}
