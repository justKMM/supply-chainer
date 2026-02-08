import React from 'react';
import type { ProfitSummary as ProfitSummaryType } from '../types';

interface ProfitSummaryProps {
  summary?: ProfitSummaryType | null;
}

const formatEur = (value: number) => `EUR ${value.toLocaleString()}`;

export const ProfitSummary: React.FC<ProfitSummaryProps> = ({ summary }) => {
  if (!summary) {
    return <div className="text-center py-6 text-text-muted"><p>No profit summary</p></div>;
  }

  return (
    <div className="grid grid-cols-2 gap-4 text-xs">
      <div>
        <div className="text-[10px] uppercase tracking-wider text-text-muted">Total Revenue</div>
        <div className="text-lg font-bold text-accent-green">{formatEur(summary.total_revenue_eur)}</div>
      </div>
      <div>
        <div className="text-[10px] uppercase tracking-wider text-text-muted">Total Cost</div>
        <div className="text-lg font-bold text-orange-400">{formatEur(summary.total_cost_eur)}</div>
      </div>
      <div>
        <div className="text-[10px] uppercase tracking-wider text-text-muted">Total Profit</div>
        <div className="text-lg font-bold text-ferrari-red">{formatEur(summary.total_profit_eur)}</div>
      </div>
      <div>
        <div className="text-[10px] uppercase tracking-wider text-text-muted">Profit / Item</div>
        <div className="text-lg font-bold text-text-primary">{formatEur(summary.profit_per_item_eur)}</div>
      </div>
      <div>
        <div className="text-[10px] uppercase tracking-wider text-text-muted">Quantity</div>
        <div className="text-lg font-bold text-text-primary">{summary.quantity}</div>
      </div>
      <div>
        <div className="text-[10px] uppercase tracking-wider text-text-muted">Margin</div>
        <div className="text-lg font-bold text-accent-blue">{summary.margin_pct.toFixed(2)}%</div>
      </div>
    </div>
  );
};
