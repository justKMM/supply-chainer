import type { ReportData, LiveMessage, SupplierSummary } from '../types';
import { MetricsGrid } from './MetricsGrid';
import { NetworkGraph } from './NetworkGraph';
import { Feed } from './Feed';
import { SupplierMap } from './Map';
import { CostChart } from './CostChart';
import { Timeline } from './Timeline';
import { Negotiations } from './Negotiations';
import { Risks } from './Risks';
import { Compliance } from './Compliance';
import { Discovery } from './Discovery';
import { Intelligence } from './Intelligence';
import { PubSub } from './PubSub';
import { Reputation } from './Reputation';
import { Reasoning } from './Reasoning';
import { ProfitSummary } from './ProfitSummary';
import { PolicyEvaluation } from './PolicyEvaluation';
import { IntentExpansion } from './IntentExpansion';
import { EventLog } from './EventLog';
import { Suppliers } from './Suppliers';

interface DashboardProps {
  data: ReportData;
  messages: LiveMessage[];
  messageCount: number;
  suppliers: SupplierSummary[];
  suppliersError?: string | null;
}

export const Dashboard: React.FC<DashboardProps> = ({
  data,
  messages,
  messageCount,
  suppliers,
  suppliersError,
}) => {
  const nodeCount = data.graph_nodes?.length || 0;
  const edgeCount = data.graph_edges?.length || 0;
  const intelCount = data.intelligence_feed?.length || 0;
  const subCount = data.pubsub_summary?.subscriptions?.length || 0;
  const repCount = data.reputation_summary?.total_agents_scored || 0;
  const reasoningCount = data.reasoning_log?.length || 0;
  const overallRisk = data.execution_plan?.risk_assessment?.overall_risk || 'medium';
  const eventCount = data.event_log?.length || 0;

  const getRiskBadgeStyles = (risk: string) => {
    switch (risk) {
      case 'high': return 'bg-red-500/20 text-red-500';
      case 'medium': return 'bg-orange-500/20 text-orange-500';
      default: return 'bg-green-500/20 text-green-500';
    }
  };

  return (
    <div className="px-5 py-6 md:px-10 md:py-8">
      {/* Hero Metrics */}
      <div className="mb-7">
        <div className="section-title"><span className="dot"></span> Key Metrics</div>
        <MetricsGrid metrics={data.dashboard?.hero_metrics || []} />
      </div>

      {/* Row 0: Profit + Policy + Intent */}
      <div className="grid grid-cols-1 gap-5 mb-7 md:grid-cols-3">
        <div className="card">
          <div className="card-header">Profit Summary</div>
          <div className="card-body">
            <ProfitSummary summary={data.profit_summary} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">Policy Evaluation</div>
          <div className="card-body">
            <PolicyEvaluation evaluation={data.policy_evaluation} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">Intent Expansion</div>
          <div className="card-body">
            <IntentExpansion expansion={data.intent_expansion} />
          </div>
        </div>
      </div>

      {/* Row 1: Network Graph + Live Feed */}
      <div className="grid grid-cols-1 gap-5 mb-7 md:grid-cols-2">
        <div className="card">
          <div className="card-header">
            <span>Supply Network Graph</span>
            <span className="text-[11px] text-text-muted">{nodeCount} agents, {edgeCount} connections</span>
          </div>
          <div className="p-0 card-body">
            <NetworkGraph nodes={data.graph_nodes || []} edges={data.graph_edges || []} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <span>Live Agent Communication</span>
            <span className="text-[11px] text-text-muted">{messageCount} messages</span>
          </div>
          <div className="p-0 card-body">
            <Feed messages={messages} />
          </div>
        </div>
      </div>

      {/* Row 2: Map + Cost Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-[2fr_1fr] gap-5 mb-7">
        <div className="card">
          <div className="card-header">Supplier Network Map</div>
          <div className="p-0 card-body">
            <SupplierMap 
              markers={data.dashboard?.supplier_markers || []} 
              routes={data.dashboard?.supplier_routes || []} 
            />
          </div>
        </div>
        <div className="card">
          <div className="card-header">Cost Breakdown</div>
          <div className="card-body">
            <CostChart items={data.dashboard?.cost_breakdown || []} />
          </div>
        </div>
      </div>

      {/* Row 3: Timeline + Negotiations */}
      <div className="grid grid-cols-1 gap-5 mb-7 md:grid-cols-2">
        <div className="card">
          <div className="card-header">Procurement Timeline</div>
          <div className="p-0 card-body">
            <Timeline items={data.dashboard?.timeline_items || []} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">Negotiation Summary</div>
          <div className="p-0 overflow-y-auto card-body max-h-[350px]">
            <Negotiations items={data.negotiations || []} />
          </div>
        </div>
      </div>

      {/* Row 4: Risk + Compliance + Discovery */}
      <div className="grid grid-cols-1 gap-5 mb-7 md:grid-cols-3">
        <div className="card">
          <div className="card-header">
            <span>Risk Assessment</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${getRiskBadgeStyles(overallRisk)}`}>
              {overallRisk.toUpperCase()}
            </span>
          </div>
          <div className="p-0 card-body">
            <Risks risks={data.dashboard?.risk_items || []} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">Compliance Summary</div>
          <div className="p-0 card-body">
            <Compliance summary={data.compliance_summary || {}} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">Discovery Paths</div>
          <div className="p-0 overflow-y-auto card-body max-h-[300px]">
            <Discovery paths={data.discovery_results?.discovery_paths || []} stats={{
              discovered: data.discovery_results?.agents_discovered || 0,
              qualified: data.discovery_results?.agents_qualified || 0,
              disqualified: data.discovery_results?.agents_disqualified || 0
            }} />
          </div>
        </div>
      </div>

      {/* Row 5: Intelligence Feed + Pub-Sub */}
      <div className="grid grid-cols-1 gap-5 mb-7 md:grid-cols-2">
        <div className="card">
          <div className="card-header">
            <span>Network Intelligence Feed</span>
            <span className="text-[11px] text-text-muted">{intelCount} signals</span>
          </div>
          <div className="p-0 overflow-y-auto card-body max-h-[450px]">
            <Intelligence signals={data.intelligence_feed || []} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <span>Event Subscriptions (Pub-Sub)</span>
            <span className="text-[11px] text-text-muted">{subCount} agents</span>
          </div>
          <div className="p-0 overflow-y-auto card-body max-h-[450px]">
            <PubSub summary={data.pubsub_summary || {}} />
          </div>
        </div>
      </div>

      {/* Row 6: Event Log */}
      <div className="mb-7">
        <div className="card">
          <div className="card-header">
            <span>Dynamic Event Log</span>
            <span className="text-[11px] text-text-muted">{eventCount} events</span>
          </div>
          <div className="p-0 overflow-y-auto card-body max-h-[360px]">
            <EventLog events={data.event_log || []} />
          </div>
        </div>
      </div>

      {/* Row 7: Supplier Directory */}
      <div className="mb-7">
        <div className="card">
          <div className="card-header">
            <span>Supplier Directory</span>
            <span className="text-[11px] text-text-muted">{suppliers.length} suppliers</span>
          </div>
          <div className="p-0 overflow-y-auto card-body max-h-[360px]">
            <Suppliers suppliers={suppliers} error={suppliersError} />
          </div>
        </div>
      </div>

      {/* Row 8: Reputation Leaderboard */}
      <div className="mb-7">
        <div className="card">
          <div className="card-header">
            <span>Verifiable Reputation Leaderboard</span>
            <span className="text-[11px] text-text-muted">{repCount} agents | {data.reputation_summary?.total_attestations || 0} attestations</span>
          </div>
          <div className="p-0 card-body">
            <Reputation summary={data.reputation_summary || {}} />
          </div>
        </div>
      </div>

      {/* Row 9: Agent Reasoning Log */}
      <div className="mb-7">
        <div className="card">
          <div className="card-header">
            <span>Agent Reasoning Log (AI-Powered Decisions)</span>
            <span className="text-[11px] text-text-muted">{reasoningCount} decisions</span>
          </div>
          <div className="p-0 card-body">
            <Reasoning logs={data.reasoning_log || []} />
          </div>
        </div>
      </div>
    </div>
  );
};