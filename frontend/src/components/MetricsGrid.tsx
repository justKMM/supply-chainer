import React from 'react';
import type { HeroMetric } from '../types';
import { MetricCard } from './MetricCard';

interface MetricsGridProps {
  metrics: HeroMetric[];
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  return (
    <div className="grid gap-[14px] grid-cols-[repeat(auto-fit,minmax(170px,1fr))]">
      {metrics.map((m, idx) => (
        <MetricCard key={idx} {...m} />
      ))}
    </div>
  );
};