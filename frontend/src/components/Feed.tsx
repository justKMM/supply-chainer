import React from 'react';
import type { LiveMessage } from '../types';
import { TYPE_COLORS, TYPE_ICONS } from '../constants';

interface FeedProps {
  messages: LiveMessage[];
}

export const Feed: React.FC<FeedProps> = ({ messages }) => {
  return (
    <div className="overflow-y-auto max-h-[420px]">
      {messages.map((msg, idx) => {
        const color = TYPE_COLORS[msg.type] || '#666';
        const icon = TYPE_ICONS[msg.type] || '\u2139\uFE0F';
        const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : '';

        return (
          <div key={`${msg.message_id}-${idx}`} className="px-4 py-2.5 border-b border-border/50 text-xs animate-[fadeIn_0.3s_ease] hover:bg-white/5 transition-colors">
            <div className="flex items-center gap-1.5 mb-1">
              <span>{icon}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-[0.5px]" style={{
                background: `${color}22`, color: color
              }}>{msg.type.replace(/_/g, ' ')}</span>
              <span className="font-semibold text-text-primary">{msg.from_label || msg.from_id || ''}</span>
              <span className="text-[10px] text-text-muted">→</span>
              <span className="text-text-secondary">{msg.to_label || msg.to_id || ''}</span>
              <span className="ml-auto text-[10px] text-text-muted">{time}</span>
            </div>
            <div className="mt-[3px] leading-snug text-text-primary">{msg.summary || ''}</div>
            {msg.detail && <div className="mt-0.5 text-[11px] text-text-muted">{msg.detail}</div>}
          </div>
        );
      })}
    </div>
  );
};