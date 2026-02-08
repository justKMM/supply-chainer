import { elements } from '../dom.js';
import { state } from '../state.js';

export function renderNetworkGraph(report) {
  const nodes = (report.graph_nodes || []).map(n => ({
    id: n.id,
    label: n.label,
    color: { background: n.color, border: n.color, highlight: { background: n.color, border: '#fff' } },
    size: n.size || 25,
    font: { color: '#ddd', size: 11, face: 'Inter' },
    shape: n.role === 'procurement_agent' ? 'diamond' :
           n.role === 'logistics_provider' ? 'triangle' :
           n.role === 'compliance_agent' ? 'square' :
           n.role === 'assembly_coordinator' ? 'star' : 'dot',
    title: `${n.label}\nRole: ${n.role}\nTrust: ${n.trust_score || 'N/A'}`,
  }));

  const edges = (report.graph_edges || []).map(e => ({
    from: e.from,
    to: e.to,
    label: e.label || '',
    color: { color: e.type === 'procurement' ? '#DC143C44' :
                   e.type === 'logistics' ? '#9C27B044' :
                   e.type === 'compliance' ? '#FF980044' : '#2196F344',
             highlight: '#fff' },
    width: e.type === 'procurement' ? 2 : 1,
    font: { color: '#666', size: 9, face: 'Inter' },
    arrows: 'to',
    smooth: { type: 'curvedCW', roundness: 0.2 },
    title: `${e.type}: ${e.label}\n${e.value_eur ? 'EUR ' + e.value_eur.toLocaleString() : ''}`,
  }));

  elements.nodeCount().textContent = `${nodes.length} agents, ${edges.length} connections`;

  const container = elements.networkGraph();
  const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
  const options = {
    physics: {
      stabilization: { iterations: 100 },
      barnesHut: { gravitationalConstant: -3000, centralGravity: 0.3, springLength: 150 }
    },
    interaction: { hover: true, tooltipDelay: 200 },
    layout: { improvedLayout: true },
  };

  if (state.networkInstance) state.networkInstance.destroy();
  state.networkInstance = new vis.Network(container, data, options);
}
