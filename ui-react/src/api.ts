import type { ProgressData, ReportData } from './types';

export async function triggerCascadeRequest(): Promise<void> {
  await fetch('/registry/trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      intent: 'Buy all parts required to assemble one Ferrari 296 GTB',
      budget_eur: 500000,
    }),
  });
}

export async function fetchProgress(): Promise<ProgressData> {
  const resp = await fetch('/api/progress');
  if (!resp.ok) {
    throw new Error('Failed to fetch progress');
  }
  return resp.json();
}

export async function fetchReport(): Promise<ReportData> {
  const resp = await fetch('/api/report');
  if (!resp.ok) {
    throw new Error('Failed to fetch report');
  }
  return resp.json();
}
