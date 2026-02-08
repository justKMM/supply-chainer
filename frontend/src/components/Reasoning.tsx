import React from 'react';
import type { ReasoningItem } from '../types';

interface ReasoningProps {
  logs: ReasoningItem[];
}

export const Reasoning: React.FC<ReasoningProps> = ({ logs }) => {
  if (!logs.length) {
    return <div className="text-center py-8 text-text-muted"><p>No reasoning data</p></div>;
  }

  return (
    <div className="overflow-y-auto max-h-[350px]">
      {logs.map((r, idx) => (
        <div key={idx} className="px-4 py-2.5 border-b border-border/50 text-xs">
          <div className={`font-semibold mb-0.5 flex items-center gap-1.5 ${
            r.agent.includes('Ferrari') ? 'text-ferrari-red' : 'text-accent-blue'
          }`}>
            {r.agent}
          </div>
          <div className="text-text-secondary leading-relaxed italic">
            "{r.thought}"
          </div>
        </div>
      ))}
    </div>
  );
};