import React from 'react';
import type { PubSubSummary } from '../types';

interface PubSubProps {
  summary: PubSubSummary;
}

export const PubSub: React.FC<PubSubProps> = ({ summary }) => {
  const subs = summary.subscriptions || [];

  return (
    <div id="pubsubContainer">
      <div className="flex gap-4 mt-2 px-4 py-3 border-b border-border">
        <div className="text-center">
          <div className="text-xl font-extrabold text-cyan-500">{summary.total_events || 0}</div>
          <div className="text-[9px] text-text-muted uppercase">Events</div>
        </div>
        <div className="text-center">
          <div className="text-xl font-extrabold text-cyan-500">{summary.total_subscriptions || 0}</div>
          <div className="text-[9px] text-text-muted uppercase">Subscribers</div>
        </div>
        <div className="text-center">
          <div className="text-xl font-extrabold text-cyan-500">{summary.total_deliveries || 0}</div>
          <div className="text-[9px] text-text-muted uppercase">Deliveries</div>
        </div>
      </div>
      {subs.length === 0 ? (
        <div className="text-center py-8 text-text-muted"><p>No subscriptions</p></div>
      ) : (
        subs.map((s, idx) => (
          <div key={idx} className="px-4 py-2 border-b border-border/30 text-xs">
            <div className="font-semibold text-text-primary">{s.agent_name || s.agent_id}</div>
            <div className="flex flex-wrap gap-1 mt-1">
              {(s.categories || []).map((c, i) => (
                <span key={i} className="px-1.5 py-px rounded text-[9px] font-semibold uppercase bg-cyan-500/15 text-cyan-500">
                  {c.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
};