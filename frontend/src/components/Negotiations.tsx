import React from 'react';
import type { NegotiationItem } from '../types';

interface NegotiationsProps {
  items: NegotiationItem[];
}

export const Negotiations: React.FC<NegotiationsProps> = ({ items }) => {
  if (!items.length) {
    return <div className="text-center py-8 text-text-muted"><p>No negotiations yet</p></div>;
  }

  return (
    <div id="negotiationContainer">
      {items.map((n, idx) => (
        <div key={idx} className="px-4 py-3.5 border-b border-border/50">
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="text-[13px] font-semibold">{n.product}</div>
              <div className="text-xs text-text-secondary">{n.with_name || n.with_agent}</div>
            </div>
            <span className="bg-green-500/20 text-green-500 px-2 py-0.5 rounded text-[10px] font-bold">
              {n.rounds} rounds
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex flex-col items-center px-2.5 py-1.5 bg-white/5 rounded-md text-[11px]">
              <span className="text-[9px] text-text-muted uppercase">Ask</span>
              <span className="text-[13px] font-bold text-red-500">EUR {n.initial_ask_eur?.toLocaleString()}</span>
            </div>
            <span className="text-base text-text-muted">→</span>
            <div className="flex flex-col items-center px-2.5 py-1.5 bg-white/5 rounded-md text-[11px]">
              <span className="text-[9px] text-text-muted uppercase">Offer</span>
              <span className="text-[13px] font-bold text-orange-500">EUR {n.initial_offer_eur?.toLocaleString()}</span>
            </div>
            <span className="text-base text-text-muted">→</span>
            <div className="flex flex-col items-center px-2.5 py-1.5 bg-white/5 rounded-md text-[11px]">
              <span className="text-[9px] text-text-muted uppercase">Agreed</span>
              <span className="text-[13px] font-bold text-green-500">EUR {n.final_agreed_eur?.toLocaleString()}</span>
            </div>
          </div>
          <div className="mt-1.5 text-[11px] text-accent-green">
            Discount: {n.discount_pct?.toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  );
};