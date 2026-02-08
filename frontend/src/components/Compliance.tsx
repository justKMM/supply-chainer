import React from 'react';
import type { ComplianceSummary } from '../types';

interface ComplianceProps {
  summary: ComplianceSummary;
}

export const Compliance: React.FC<ComplianceProps> = ({ summary }) => {
  return (
    <div id="complianceContainer">
      <div className="grid grid-cols-4 gap-2.5 p-3">
        <div className="text-center p-3 bg-white/5 rounded-lg">
          <div className="text-[28px] font-extrabold text-accent-blue">{summary.total_checks || 0}</div>
          <div className="text-[10px] text-text-muted uppercase mt-1">Total Checks</div>
        </div>
        <div className="text-center p-3 bg-white/5 rounded-lg">
          <div className="text-[28px] font-extrabold text-accent-green">{summary.passed || 0}</div>
          <div className="text-[10px] text-text-muted uppercase mt-1">Passed</div>
        </div>
        <div className="text-center p-3 bg-white/5 rounded-lg">
          <div className="text-[28px] font-extrabold text-accent-orange">{summary.flagged || 0}</div>
          <div className="text-[10px] text-text-muted uppercase mt-1">Flagged</div>
        </div>
        <div className="text-center p-3 bg-white/5 rounded-lg">
          <div className="text-[28px] font-extrabold text-red-500">{summary.failed || 0}</div>
          <div className="text-[10px] text-text-muted uppercase mt-1">Failed</div>
        </div>
      </div>
      {(summary.flags || []).map((f, idx) => (
        <div key={idx} className="px-4 py-3 border-b border-border/50">
          <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase mr-2 bg-orange-500/20 text-orange-500">
            WARNING
          </span>
          <span className="text-[13px] font-semibold inline">{f.agent_id}</span>
          <div className="mt-1 text-[11px] text-text-muted">{f.detail}</div>
        </div>
      ))}
    </div>
  );
};