import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import type { CostItem } from '../types';

ChartJS.register(ArcElement, Tooltip, Legend);

interface CostChartProps {
  items: CostItem[];
}

export const CostChart: React.FC<CostChartProps> = ({ items }) => {
  const data = {
    labels: items.map(i => i.label),
    datasets: [{
      data: items.map(i => i.value),
      backgroundColor: items.map(i => i.color),
      borderWidth: 0,
      hoverOffset: 8,
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: { color: '#888', font: { size: 11, family: 'Inter' }, padding: 12 }
      },
      tooltip: {
        callbacks: {
          label: (ctx: any) => `${ctx.label}: EUR ${ctx.parsed.toLocaleString()}`
        }
      }
    }
  };

  return (
    <div className="relative h-[250px]">
      <Doughnut data={data} options={options} />
    </div>
  );
};