import React from 'react';
import type { IntelligenceSignal } from '../types';

interface IntelligenceProps {
  signals: IntelligenceSignal[];
}

export const Intelligence: React.FC<IntelligenceProps> = ({ signals }) => {
  if (!signals.length) {
    return <div className="text-center py-8 text-text-muted"><p>No intelligence signals</p></div>;
  }

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-700/20 text-red-700';
      case 'high': return 'bg-red-500/20 text-red-500';
      case 'medium': return 'bg-orange-500/20 text-orange-500';
      default: return 'bg-green-500/20 text-green-500';
    }
  };

  return (
    <div id="intelContainer">
      {signals.map((s, idx) => {
        const evt = s.event || {};
        const severity = evt.severity || 'medium';
        const actions = (evt.recommended_actions || []).slice(0, 3);
        
        return (
          <div key={idx} className="px-4 py-3 border-b border-border/50">
            <div className="flex items-center gap-2 mb-1.5">
              <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${getSeverityStyles(severity)}`}>
                {severity}
              </span>
              <span className="px-1.5 py-px rounded text-[9px] font-semibold uppercase bg-cyan-500/15 text-cyan-500">
                {(evt.category || '').replace(/_/g, ' ')}
              </span>
              <span className="text-[10px] text-text-muted">{evt.source || ''}</span>
            </div>
            <div className="text-[13px] font-semibold text-text-primary">{evt.title || ''}</div>
            <div className="text-[11px] text-text-secondary my-1 leading-relaxed">{evt.description || ''}</div>
            {actions.length > 0 && (
              <div className="text-[11px] text-accent-blue mt-1">
                Recommended: {actions.join(' | ')}
              </div>
            )}
            <div className="text-[10px] text-text-muted mt-1">Delivered to {s.recipient_count || 0} subscribed agents</div>
            {s.ai_reaction && (
              <div className="mt-1.5 px-3 py-2 bg-[rgba(220,20,60,0.05)] border-l-[3px] border-ferrari-red rounded-r-md text-[11px] text-text-secondary italic">
                Ferrari Procurement: "{s.ai_reaction}"
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};