import React from 'react';
import type { TimelineItem } from '../types';

interface TimelineProps {
  items: TimelineItem[];
}

const CAT_COLORS: Record<string, string> = {
  powertrain: '#DC143C', braking_system: '#2196F3', body_chassis: '#4CAF50',
  electronics: '#FF9800', interior: '#9C27B0', suspension: '#00BCD4',
  wheels_tires: '#FFC107', exhaust_emissions: '#F44336',
};

export const Timeline: React.FC<TimelineProps> = ({ items }) => {
  if (!items.length) {
    return <div className="text-center py-8 text-text-muted"><p>No timeline data</p></div>;
  }

  const maxDays = Math.max(...items.map(i => i.lead_time_days || 14));

  return (
    <div className="py-2">
      {items.map((item, idx) => {
        const days = item.lead_time_days || 14;
        const widthPct = (days / (maxDays + 5)) * 100;
        const color = CAT_COLORS[item.category] || '#2196F3';
        
        return (
          <div key={idx} className="flex items-center gap-3 px-4 py-1.5 text-xs">
            <div 
              className="w-[200px] min-w-[200px] text-text-secondary whitespace-nowrap overflow-hidden text-ellipsis" 
              title={item.label}
            >
              {item.label}
            </div>
            <div className="flex-1 h-[22px] relative bg-white/5 rounded-md">
              <div 
                className={`absolute h-full rounded-md flex items-center justify-center text-[10px] font-semibold text-white min-w-[30px] left-0 ${item.critical_path ? 'shadow-[0_0_8px_rgba(244,67,54,0.5)]' : ''}`}
                style={{
                  width: `${widthPct}%`, 
                  background: color
                }}
              >
                {days}d
              </div>
            </div>
            <div className="w-[60px] text-right text-text-muted text-[11px]">{days} days</div>
          </div>
        );
      })}
    </div>
  );
};