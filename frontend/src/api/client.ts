import type { AgentFact, CascadeReport, CascadeProgress, LiveMessage } from "@/data/types";

const BASE = "";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init);
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

// ── Registry ────────────────────────────────────────────────────────────────

export function listAgents(): Promise<AgentFact[]> {
  return fetchJSON("/registry/list");
}

export function getAgent(agentId: string): Promise<AgentFact> {
  return fetchJSON(`/registry/agent/${agentId}`);
}

export function searchAgents(params: {
  role?: string;
  capability?: string;
  region?: string;
  min_trust?: number;
}): Promise<AgentFact[]> {
  const qs = new URLSearchParams();
  if (params.role) qs.set("role", params.role);
  if (params.capability) qs.set("capability", params.capability);
  if (params.region) qs.set("region", params.region);
  if (params.min_trust) qs.set("min_trust", String(params.min_trust));
  return fetchJSON(`/registry/search?${qs}`);
}

// ── Cascade ─────────────────────────────────────────────────────────────────

export function triggerCascade(intent: string, budgetEur: number) {
  return fetchJSON<{ status: string; intent: string }>("/registry/trigger", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ intent, budget_eur: budgetEur }),
  });
}

export function getProgress(): Promise<CascadeProgress> {
  return fetchJSON("/api/progress");
}

export function getReport(): Promise<CascadeReport> {
  return fetchJSON("/api/report");
}

// ── Messages ────────────────────────────────────────────────────────────────

export function getLogs(): Promise<LiveMessage[]> {
  return fetchJSON("/registry/logs");
}

// ── Reputation ──────────────────────────────────────────────────────────────

export function getReputationSummary() {
  return fetchJSON<{
    total_agents_scored: number;
    total_attestations: number;
    leaderboard: Array<{
      agent_id: string;
      agent_name: string;
      composite_score: number;
      total_attestations: number;
    }>;
  }>("/api/reputation/summary");
}

export function getReputationScores() {
  return fetchJSON<Array<{
    agent_id: string;
    agent_name: string;
    composite_score: number;
    total_attestations: number;
  }>>("/api/reputation/scores");
}

// ── Pub-Sub ─────────────────────────────────────────────────────────────────

export function getPubsubSummary() {
  return fetchJSON("/api/pubsub/summary");
}

export function getPubsubEvents() {
  return fetchJSON("/api/pubsub/events");
}

// ── SSE Stream ──────────────────────────────────────────────────────────────

export function subscribeToStream(
  onMessage: (msg: LiveMessage) => void,
  onError?: (err: Event) => void,
): EventSource {
  const es = new EventSource(`${BASE}/api/stream`);
  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as LiveMessage;
      if (data.type === "heartbeat") return;
      onMessage(data);
    } catch {
      // ignore parse errors
    }
  };
  if (onError) es.onerror = onError;
  return es;
}
