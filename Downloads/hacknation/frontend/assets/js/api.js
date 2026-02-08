export async function triggerCascadeRequest() {
  return fetch('/registry/trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      intent: 'Buy all parts required to assemble one Ferrari 296 GTB',
      budget_eur: 500000,
    }),
  });
}

export async function fetchProgress() {
  const resp = await fetch('/api/progress');
  return resp.json();
}

export async function fetchReport() {
  const resp = await fetch('/api/report');
  return resp.json();
}
