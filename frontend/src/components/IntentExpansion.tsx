import React from 'react';
import type { IntentExpansion as IntentExpansionType } from '../types';

interface IntentExpansionProps {
  expansion?: IntentExpansionType | null;
}

const Section: React.FC<{ title: string; items: string[] }> = ({ title, items }) => (
  <div className="mb-3">
    <div className="text-[10px] uppercase tracking-wider text-text-muted mb-1">{title}</div>
    {items.length ? (
      <ul className="space-y-1 text-xs">
        {items.map((item, idx) => (
          <li key={idx} className="px-2 py-1 rounded bg-bg-secondary border border-border/40">
            {item}
          </li>
        ))}
      </ul>
    ) : (
      <div className="text-xs text-text-muted">No items</div>
    )}
  </div>
);

export const IntentExpansion: React.FC<IntentExpansionProps> = ({ expansion }) => {
  if (!expansion) {
    return <div className="text-center py-6 text-text-muted"><p>No intent expansion</p></div>;
  }

  return (
    <div className="text-xs">
      <div className="mb-3">
        <div className="text-[10px] uppercase tracking-wider text-text-muted mb-1">Root Intent</div>
        <div className="px-3 py-2 rounded bg-bg-secondary border border-border/40">{expansion.root_intent}</div>
      </div>
      <Section title="Component Intents" items={expansion.component_intents || []} />
      <Section title="Logistics Intents" items={expansion.logistics_intents || []} />
      <Section title="Compliance Intents" items={expansion.compliance_intents || []} />
    </div>
  );
};
