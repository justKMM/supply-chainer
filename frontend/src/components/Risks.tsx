import React from 'react';
import type { RiskItem } from '../types';

interface RisksProps {
  risks: RiskItem[];
}

export const Risks: React.FC<RisksProps> = ({ risks }) => {
  if (!risks.length) {
    return <div className="text-center py-8 text-text-muted"><p>No risks identified</p></div>;
  }

  return (
    <div id="riskContainer">
      {risks.map((r, idx) => (
        <div key={idx} className="px-4 py-3 border-b border-border/50">
          <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase mr-2 ${
            r.type === 'single_source_dependency' 
              ? 'bg-red-500/20 text-red-500' 
              : 'bg-green-500/20 text-green-500'
          }`}>
            {r.type === 'single_source_dependency' ? 'HIGH' : 'LOW'}
          </span>
          <span className="text-[13px] font-semibold inline">
            {r.type?.replace(/_/g, ' ')}: {r.component || ''}
          </span>
          <div className="mt-1 text-[11px] text-text-muted">
            {r.detail || r.supplier || ''}
          </div>
          <div className="mt-0.5 text-[11px] text-accent-green">
            → {r.mitigation || ''}
          </div>
        </div>
      ))}
    </div>
  );
};