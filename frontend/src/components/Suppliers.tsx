import React from 'react';
import type { SupplierSummary } from '../types';

interface SuppliersProps {
  suppliers: SupplierSummary[];
  error?: string | null;
}

export const Suppliers: React.FC<SuppliersProps> = ({ suppliers, error }) => {
  if (error) {
    return <div className="text-center py-6 text-text-muted"><p>{error}</p></div>;
  }

  if (!suppliers.length) {
    return <div className="text-center py-6 text-text-muted"><p>No suppliers loaded</p></div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-xs">
        <thead>
          <tr>
            {['Agent', 'Role', 'Location', 'Trust'].map((h) => (
              <th key={h} className="text-left px-3 py-2 text-[10px] uppercase tracking-wider text-text-muted border-b border-border">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {suppliers.map((s) => (
            <tr key={s.agent_id} className="border-b border-border/30">
              <td className="px-3 py-2 font-semibold">{s.name || s.agent_id}</td>
              <td className="px-3 py-2 text-text-muted">{s.role}</td>
              <td className="px-3 py-2 text-text-muted">
                {s.location?.headquarters?.city || '—'}{s.location?.headquarters?.country ? `, ${s.location.headquarters.country}` : ''}
              </td>
              <td className="px-3 py-2">
                {s.trust?.trust_score !== undefined ? `${(s.trust.trust_score * 100).toFixed(0)}%` : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
