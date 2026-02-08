import { useEffect, useRef } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
import type { GraphNode, GraphEdge } from '../types';

interface NetworkGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({ nodes, edges }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const visNodes = new DataSet(
      nodes.map(n => ({
        id: n.id,
        label: n.label,
        color: { background: n.color, border: n.color, highlight: { background: n.color, border: '#fff' } },
        size: n.size || 25,
        font: { color: '#ddd', size: 11, face: 'Inter' },
        shape: n.role === 'procurement_agent' ? 'diamond' :
               n.role === 'logistics_provider' ? 'triangle' :
               n.role === 'compliance_agent' ? 'square' :
               n.role === 'assembly_coordinator' ? 'star' : 'dot',
        title: `${n.label}\nRole: ${n.role}\nTrust: ${n.trust_score ?? 'N/A'}\nRisk: ${n.risk_score ?? 'N/A'}`, 
      }))
    );

    const visEdges = new DataSet(
      edges.map((e, idx) => ({
        id: `edge-${idx}`,
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
        smooth: { enabled: true, type: 'curvedCW', roundness: 0.2 },
        title: `${e.type}: ${e.label}\n${e.value_eur ? 'EUR ' + e.value_eur.toLocaleString() : ''}${e.risk_level ? `\nRisk: ${e.risk_level}` : ''}`,
      }))
    );
    
    // @ts-ignore
    const data = { nodes: visNodes, edges: visEdges };

    const options = {
      physics: {
        stabilization: { iterations: 100 },
        barnesHut: { gravitationalConstant: -3000, centralGravity: 0.3, springLength: 150 }
      },
      interaction: { hover: true, tooltipDelay: 200 },
      layout: { improvedLayout: true },
      height: '100%',
      width: '100%',
    };

    if (networkRef.current) {
      networkRef.current.setData(data);
    } else {
      networkRef.current = new Network(containerRef.current, data, options);
    }

  }, [nodes, edges]);

  return <div ref={containerRef} className="w-full h-[420px]" />;
};