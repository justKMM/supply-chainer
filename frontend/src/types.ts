export interface HeroMetric {
  label: string;
  value: string;
  trend?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  role: string;
  color: string;
  trust_score?: number;
  risk_score?: number;
  size?: number;
}

export interface GraphEdge {
  from: string;
  to: string;
  type: string;
  label: string;
  value_eur?: number;
  risk_level?: number;
}

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
  color?: string;
  icon?: string;
}

export interface CostItem {
  label: string;
  value: number;
  color: string;
}

export interface TimelineItem {
  label: string;
  lead_time_days: number;
  critical_path: boolean;
  category: string;
}

export interface MapMarker {
  lat: number;
  lon: number;
  label: string;
  type: string;
  color: string;
}

export interface MapRoute {
  from: { lat: number; lon: number };
  to: { lat: number; lon: number };
}

export interface NegotiationItem {
  product: string;
  with_name?: string;
  with_agent?: string;
  rounds: number;
  initial_ask_eur?: number;
  initial_offer_eur?: number;
  final_agreed_eur?: number;
  discount_pct?: number;
}

export interface RiskItem {
  type: string;
  component?: string;
  supplier?: string;
  detail?: string;
  mitigation?: string;
}

export interface ComplianceFlag {
  agent_id: string;
  detail: string;
}

export interface ComplianceSummary {
  total_checks: number;
  passed: number;
  flagged: number;
  failed: number;
  flags: ComplianceFlag[];
}

export interface DiscoveryPath {
  need: string;
  query: string;
  selected: string;
  results_count: number;
}

export interface IntelligenceSignal {
  event: {
    severity: string;
    category: string;
    source: string;
    title: string;
    description: string;
    recommended_actions: string[];
  };
  recipient_count: number;
  ai_reaction?: string;
}

export interface PubSubSubscription {
  agent_id: string;
  agent_name: string;
  categories: string[];
}

export interface PubSubSummary {
  total_events: number;
  total_subscriptions: number;
  total_deliveries: number;
  subscriptions: PubSubSubscription[];
}

export interface ReputationScore {
  agent_id: string;
  agent_name: string;
  composite_score: number;
  delivery: number;
  quality: number;
  pricing: number;
  compliance: number;
  reliability: number;
  transactions: number;
  trend: 'improving' | 'stable' | 'declining';
}

export interface ChainVerification {
  valid: boolean;
  length: number;
}

export interface ReputationSummary {
  total_agents_scored: number;
  total_attestations: number;
  leaderboard: ReputationScore[];
  chain_verifications: Record<string, ChainVerification>;
}

export interface ReasoningItem {
  agent: string;
  thought: string;
}

export interface CatalogueProduct {
  product_id: string;
  name: string;
  description?: string;
  selling_price_eur: number;
  intent_template?: string;
  currency?: string;
}

export interface ProfitSummary {
  total_revenue_eur: number;
  total_cost_eur: number;
  total_profit_eur: number;
  profit_per_item_eur: number;
  quantity: number;
  margin_pct: number;
}

export interface PolicySpec {
  jurisdiction: string;
  max_risk_score: number;
  min_trust_score: number;
  min_esg_score: number;
  forbid_single_supplier: boolean;
}

export interface PolicyEvaluation {
  compliant: boolean;
  violations: Record<string, unknown>[];
  explanations: string[];
}

export interface IntentExpansion {
  root_intent: string;
  component_intents: string[];
  logistics_intents: string[];
  compliance_intents: string[];
}

export interface EventLogEntry {
  type: string;
  stage: string;
  impact: Record<string, number>;
}

export interface TrustSubmission {
  agent_id: string;
  dimension: string;
  score: number;
  context?: string;
  rater_id?: string;
}

export interface TrustSummary {
  agent_id: string;
  dimension: string;
  score: number;
  submissions: number;
}

export interface SupplierSummary {
  agent_id: string;
  name: string;
  role: string;
  status?: string;
  location?: {
    headquarters?: { city?: string; country?: string };
  };
  trust?: {
    trust_score?: number;
  };
}

export interface ReportData {
  dashboard: {
    hero_metrics: HeroMetric[];
    cost_breakdown: CostItem[];
    timeline_items: TimelineItem[];
    supplier_markers: MapMarker[];
    supplier_routes: MapRoute[];
    risk_items: RiskItem[];
  };
  graph_nodes: GraphNode[];
  graph_edges: GraphEdge[];
  negotiations: NegotiationItem[];
  discovery_results: {
    agents_discovered: number;
    agents_qualified: number;
    agents_disqualified: number;
    discovery_paths: DiscoveryPath[];
  };
  compliance_summary: ComplianceSummary;
  intelligence_feed: IntelligenceSignal[];
  pubsub_summary: PubSubSummary;
  reputation_summary: ReputationSummary;
  reasoning_log: ReasoningItem[];
  profit_summary?: ProfitSummary | null;
  policy_evaluation?: PolicyEvaluation | null;
  intent_expansion?: IntentExpansion | null;
  event_log?: EventLogEntry[];
  execution_plan?: {
    risk_assessment?: {
      overall_risk: string;
      risks: RiskItem[];
    }
  };
}

export interface ProgressData {
  progress: number;
  running: boolean;
}
