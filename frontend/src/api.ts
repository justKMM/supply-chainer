import type {
  CatalogueProduct,
  PolicyEvaluation,
  PolicySpec,
  ProgressData,
  ReportData,
  TrustSubmission,
  TrustSummary,
  SupplierSummary,
} from './types';

const API_BASE_URL =
  (import.meta as { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL ||
  'http://localhost:8000';

function apiUrl(path: string) {
  if (!path.startsWith('/')) return `${API_BASE_URL}/${path}`;
  return `${API_BASE_URL}${path}`;
}

async function ensureOk(resp: Response, errorMessage: string) {
  if (!resp.ok) {
    let detail = '';
    try {
      const data = await resp.json();
      detail = data?.error ? ` (${data.error})` : '';
    } catch {
      // ignore parsing errors
    }
    throw new Error(`${errorMessage}${detail}`);
  }
}

export interface TriggerCascadeParams {
  intent?: string;
  budget_eur?: number;
  product_id?: string;
  quantity?: number;
  strategy?: string;
  desired_delivery_date?: string;
}

export async function triggerCascadeRequest(params: TriggerCascadeParams): Promise<void> {
  await fetch(apiUrl('/registry/trigger'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
}

export async function fetchProgress(): Promise<ProgressData> {
  const resp = await fetch(apiUrl('/api/progress'));
  await ensureOk(resp, 'Failed to fetch progress');
  return resp.json();
}

export async function fetchReport(): Promise<ReportData> {
  const resp = await fetch(apiUrl('/api/report'));
  await ensureOk(resp, 'Failed to fetch report');
  return resp.json();
}

export async function fetchCatalogue(): Promise<CatalogueProduct[]> {
  const resp = await fetch(apiUrl('/api/catalogue'));
  await ensureOk(resp, 'Failed to fetch catalogue');
  return resp.json();
}

export async function fetchSuppliers(): Promise<SupplierSummary[]> {
  const resp = await fetch(apiUrl('/api/suppliers'));
  await ensureOk(resp, 'Failed to fetch suppliers');
  return resp.json();
}

export async function fetchPolicy(): Promise<PolicySpec> {
  const resp = await fetch(apiUrl('/api/policy'));
  await ensureOk(resp, 'Failed to fetch policy');
  return resp.json();
}

export async function evaluatePolicy(plan: Record<string, unknown>): Promise<PolicyEvaluation> {
  const resp = await fetch(apiUrl('/api/policy/evaluate'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(plan),
  });
  await ensureOk(resp, 'Failed to evaluate policy');
  return resp.json();
}

export async function fetchContextualTrust(agentId: string): Promise<TrustSummary> {
  const resp = await fetch(apiUrl(`/api/trust/contextual/${agentId}`));
  await ensureOk(resp, 'Failed to fetch contextual trust');
  return resp.json();
}

export async function submitTrustRating(payload: TrustSubmission): Promise<void> {
  const resp = await fetch(apiUrl('/api/trust/submit'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  await ensureOk(resp, 'Failed to submit trust rating');
}

export async function simulateSupplierFailure(agent_id: string): Promise<Record<string, unknown>> {
  const resp = await fetch(apiUrl('/api/simulate/supplier-failure'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent_id }),
  });
  await ensureOk(resp, 'Failed to simulate supplier failure');
  return resp.json();
}
