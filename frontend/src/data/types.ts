// ── Frontend display types ──────────────────────────────────────────────────

export type AgentRole = "Supplier" | "Manufacturer" | "Logistics" | "Retailer" | "Procurement" | string;
export type AgentStatus = "online" | "offline" | "busy" | "active";
export type EventType = "discovery" | "response" | "negotiation" | "coordination" | "execution" | string;
export type EventStatus = "completed" | "in-progress" | "pending" | "failed";

export interface Agent {
  id: string;
  name: string;
  role: AgentRole;
  status: AgentStatus;
  capabilities: string[];
  region: string;
  jurisdiction: string;
  endpoint: string;
  trustScore: number;
  lastSeen: string;
  messagesProcessed: number;
  activeContracts: number;
}

export interface CoordinationEvent {
  id: string;
  timestamp: string;
  from: string;
  to: string;
  type: EventType;
  message: string;
  status: EventStatus;
}

// ── Backend API response types ──────────────────────────────────────────────

export interface LiveMessage {
  message_id: string;
  timestamp: string;
  from_id: string;
  from_label: string;
  to_id: string;
  to_label: string;
  type: string;
  summary: string;
  detail: string;
  color: string;
  icon: string;
}

export interface HeroMetric {
  label: string;
  value: string;
  trend?: string;
}

export interface CostBreakdownItem {
  label: string;
  value: number;
  color: string;
}

export interface TimelineItem {
  label: string;
  category: string;
  lead_time_days: number;
  critical_path: boolean;
}

export interface SupplierMarker {
  lat: number;
  lon: number;
  label: string;
  color: string;
  type: string;
}

export interface RiskItem {
  type: string;
  component: string;
  detail: string;
  mitigation: string;
}

export interface Negotiation {
  product: string;
  with_name: string;
  rounds: number;
  initial_ask_eur: number;
  initial_offer_eur: number;
  final_agreed_eur: number;
  discount_pct: number;
}

export interface GraphNode {
  id: string;
  label: string;
  role: string;
  color: string;
  size: number;
  trust_score?: number;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  from: string;
  to: string;
  type: string;
  label: string;
  value_eur?: number;
  message_count: number;
}

export interface ComplianceSummary {
  total_checks: number;
  passed: number;
  flagged: number;
  failed: number;
  flags: string[];
}

export interface DiscoveryResults {
  agents_discovered: number;
  agents_qualified: number;
  agents_disqualified: number;
  discovery_paths: Record<string, string[]>;
}

export interface ReputationScore {
  agent_id: string;
  agent_name: string;
  composite_score: number;
  total_attestations: number;
}

export interface PubsubSummary {
  total_events: number;
  total_subscriptions: number;
  total_deliveries: number;
  subscriptions: Array<{ agent_id: string; agent_name: string; topics: string[] }>;
}

export interface IntelligenceFeedItem {
  event: string;
  recipient_count: number;
  ai_reaction: string;
}

export interface ReasoningLogEntry {
  agent: string;
  thought: string;
}

export interface CascadeReport {
  dashboard: {
    hero_metrics: HeroMetric[];
    cost_breakdown: CostBreakdownItem[];
    timeline_items: TimelineItem[];
    supplier_markers: SupplierMarker[];
    supplier_routes: Array<{ from: { lat: number; lon: number }; to: { lat: number; lon: number } }>;
    risk_items: RiskItem[];
  };
  graph_nodes: GraphNode[];
  graph_edges: GraphEdge[];
  negotiations: Negotiation[];
  compliance_summary: ComplianceSummary;
  discovery_results: DiscoveryResults;
  execution_plan: { risk_assessment: { overall_risk: string; risks: RiskItem[] } };
  intelligence_feed: IntelligenceFeedItem[];
  pubsub_summary: PubsubSummary;
  reputation_summary: {
    total_agents_scored: number;
    total_attestations: number;
    leaderboard: ReputationScore[];
    chain_verifications: Record<string, unknown>[];
  };
  reasoning_log: ReasoningLogEntry[];
}

export interface CascadeProgress {
  running: boolean;
  progress: number;
}

// ── Backend AgentFact (from registry) ───────────────────────────────────────

export interface AgentFact {
  agent_id: string;
  name: string;
  role: string;
  description: string;
  capabilities: {
    products: Array<{ product_id: string; name: string; category: string; unit_price_eur: number }>;
    services: string[];
    production_capacity?: { units_per_month: number; current_utilization_pct: number };
  };
  identity?: { legal_entity: string; registration_country: string };
  certifications: Array<{ type: string; description: string; issued_by: string }>;
  location?: {
    headquarters?: { lat: number; lon: number; city: string; country: string };
    manufacturing_sites: Array<{ site_id: string; city: string; country: string }>;
    shipping_regions: string[];
  };
  trust?: {
    trust_score: number;
    years_in_operation: number;
    ferrari_tier_status: string;
    past_contracts: number;
    on_time_delivery_pct: number;
  };
  status: string;
  registered_at: string;
}
