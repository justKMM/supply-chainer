import React from 'react';
import type { HeroMetric } from '../types';

export const MetricCard: React.FC<HeroMetric> = ({ value, label, trend }) => {
  return (
    <div className="p-[18px] text-center transition-all duration-300 border rounded-xl bg-bg-card border-border hover:bg-bg-card-hover">
      <div className="text-[26px] font-extrabold text-transparent bg-gradient-to-br from-white to-[#ccc] bg-clip-text">
        {value}
      </div>
      <div className="text-[11px] text-text-secondary mt-1.5 uppercase tracking-widest">
        {label}
      </div>
      {trend && (
        <div className="text-[11px] mt-1 text-accent-green">
          ↑ {trend}
        </div>
      )}
    </div>
  );
};