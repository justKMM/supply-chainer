import React from 'react';
import type { DiscoveryPath } from '../types';

interface DiscoveryProps {
  paths: DiscoveryPath[];
  stats: {
    discovered: number;
    qualified: number;
    disqualified: number;
  };
}

export const Discovery: React.FC<DiscoveryProps> = ({ paths, stats }) => {
  return (
    <div id="discoveryContainer">
      <div className="px-4 py-2.5 border-b border-border/50 text-xs">
        <span className="font-semibold text-accent-blue">{stats.discovered || 0}</span> discovered &bull;{' '}
        <span className="font-semibold text-accent-green">{stats.qualified || 0}</span> qualified &bull;{' '}
        <span className="font-semibold text-red-500">{stats.disqualified || 0}</span> disqualified
      </div>
      {paths.map((p, idx) => (
        <div key={idx} className="px-4 py-2.5 border-b border-border/50 text-xs">
          <div className="font-semibold text-text-primary">{p.need}</div>
          <div className="my-[3px] text-[11px] text-text-muted font-mono">{p.query}</div>
          <div className="text-accent-green">→ {p.selected} ({p.results_count} candidates)</div>
        </div>
      ))}
    </div>
  );
};