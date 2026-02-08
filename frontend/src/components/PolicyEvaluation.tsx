import React from 'react';
import type { PolicyEvaluation as PolicyEvaluationType } from '../types';

interface PolicyEvaluationProps {
  evaluation?: PolicyEvaluationType | null;
}

export const PolicyEvaluation: React.FC<PolicyEvaluationProps> = ({ evaluation }) => {
  if (!evaluation) {
    return <div className="text-center py-6 text-text-muted"><p>No policy evaluation</p></div>;
  }

  const statusClass = evaluation.compliant
    ? 'bg-green-500/20 text-green-500'
    : 'bg-red-500/20 text-red-500';

  return (
    <div className="text-xs">
      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${statusClass}`}>
          {evaluation.compliant ? 'Compliant' : 'Non-Compliant'}
        </span>
        <span className="text-text-muted">
          {evaluation.violations?.length || 0} violations
        </span>
      </div>
      <div className="space-y-2">
        {(evaluation.explanations || []).slice(0, 5).map((explanation, idx) => (
          <div key={idx} className="px-3 py-2 rounded bg-bg-secondary border border-border/40">
            {explanation}
          </div>
        ))}
        {evaluation.explanations?.length === 0 && (
          <div className="text-text-muted">No policy explanations</div>
        )}
      </div>
    </div>
  );
};
