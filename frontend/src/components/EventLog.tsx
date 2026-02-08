import React from 'react';
import type { EventLogEntry } from '../types';

interface EventLogProps {
  events: EventLogEntry[];
}

const formatImpact = (impact: Record<string, number>) =>
  Object.entries(impact)
    .map(([key, value]) => `${key.replace(/_/g, ' ')}: ${value.toFixed(2)}`)
    .join(' • ');

export const EventLog: React.FC<EventLogProps> = ({ events }) => {
  if (!events.length) {
    return <div className="text-center py-6 text-text-muted"><p>No events captured</p></div>;
  }

  return (
    <div className="space-y-2 text-xs">
      {events.map((event, idx) => (
        <div key={`${event.type}-${idx}`} className="px-3 py-2 rounded bg-bg-secondary border border-border/40">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-text-primary">{event.type.replace(/_/g, ' ')}</span>
            <span className="text-[10px] uppercase text-text-muted">{event.stage}</span>
          </div>
          <div className="mt-1 text-text-muted">{formatImpact(event.impact || {})}</div>
        </div>
      ))}
    </div>
  );
};
