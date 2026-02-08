import React from 'react';
import type { ReputationSummary } from '../types';

interface ReputationProps {
  summary: ReputationSummary;
}

export const Reputation: React.FC<ReputationProps> = ({ summary }) => {
  const leaderboard = summary.leaderboard || [];
  const chains = summary.chain_verifications || {};
  const trendSymbols: Record<string, string> = { improving: '↑', stable: '→', declining: '↓' };

  if (!leaderboard.length) {
    return <div className="text-center py-8 text-text-muted"><p>No reputation data</p></div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-xs">
        <thead>
          <tr>
            {['#', 'Agent', 'Composite', 'Delivery', 'Quality', 'Pricing', 'Compliance', 'Reliability', 'Txns', 'Trend', 'Chain'].map(h => (
              <th key={h} className="text-left px-3 py-2 text-[10px] uppercase tracking-wider text-text-muted border-b border-border">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((r, i) => {
            const chain = chains[r.agent_id] || {};
            const composite_pct = (r.composite_score * 100).toFixed(1);
            const barColor = r.composite_score > 0.85 ? '#4CAF50' :
                           r.composite_score > 0.65 ? '#FF9800' : '#F44336';
            
            return (
              <tr key={r.agent_id} className="border-b border-border/30">
                <td className="px-3 py-2 text-text-muted">{i + 1}</td>
                <td className="px-3 py-2"><span className="font-semibold">{r.agent_name || r.agent_id}</span></td>
                <td className="px-3 py-2">
                  <span className="inline-block h-1.5 rounded-full mr-1.5 align-middle" style={{
                    width: `${parseFloat(composite_pct) * 0.6}px`, background: barColor
                  }}></span>
                  <span className="font-bold text-[13px]" style={{ color: barColor }}>{composite_pct}%</span>
                </td>
                <td className={`px-3 py-2 ${r.delivery > 0.8 ? 'text-green-500' : 'text-orange-500'}`}>{(r.delivery * 100).toFixed(0)}%</td>
                <td className={`px-3 py-2 ${r.quality > 0.8 ? 'text-green-500' : 'text-orange-500'}`}>{(r.quality * 100).toFixed(0)}%</td>
                <td className={`px-3 py-2 ${r.pricing > 0.8 ? 'text-green-500' : 'text-orange-500'}`}>{(r.pricing * 100).toFixed(0)}%</td>
                <td className={`px-3 py-2 ${r.compliance > 0.8 ? 'text-green-500' : 'text-orange-500'}`}>{(r.compliance * 100).toFixed(0)}%</td>
                <td className={`px-3 py-2 ${r.reliability > 0.8 ? 'text-green-500' : 'text-orange-500'}`}>{(r.reliability * 100).toFixed(0)}%</td>
                <td className="px-3 py-2 text-text-muted">{r.transactions}</td>
                <td className="px-3 py-2">
                  <span className={`text-[11px] ${r.trend === 'improving' ? 'text-accent-green' : r.trend === 'declining' ? 'text-red-500' : 'text-text-muted'}`}>
                    {trendSymbols[r.trend] || '-'} {r.trend}
                  </span>
                </td>
                <td className="px-3 py-2">
                  <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${
                    chain.valid ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'
                  }`}>
                    {chain.valid ? 'Verified' : 'Invalid'} ({chain.length || 0})
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};