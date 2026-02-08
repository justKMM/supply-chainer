"""Pydantic models matching the Ferrari Supply Chain data schemas."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_id(prefix: str = "msg") -> str:
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"


# ── AgentFact (Registry Schema) ─────────────────────────────────────────────

class ProductSpec(BaseModel):
    material: Optional[str] = None
    diameter_mm: Optional[float] = None
    weight_kg: Optional[float] = None
    max_temp_celsius: Optional[float] = None
    displacement_cc: Optional[float] = None
    power_hp: Optional[float] = None
    voltage: Optional[float] = None

class Product(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    specifications: dict = Field(default_factory=dict)
    unit_price_eur: float
    currency: str = "EUR"
    min_order_quantity: int = 1
    lead_time_days: int = 14

class ProductionCapacity(BaseModel):
    units_per_month: int
    current_utilization_pct: float

class Capabilities(BaseModel):
    products: list[Product] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    production_capacity: Optional[ProductionCapacity] = None

class Identity(BaseModel):
    legal_entity: str
    registration_country: str
    vat_id: Optional[str] = None
    duns_number: Optional[str] = None

class Certification(BaseModel):
    type: str
    description: str = ""
    issued_by: str = ""
    valid_until: Optional[str] = None
    status: str = "active"

class Location(BaseModel):
    lat: float
    lon: float
    city: str = ""
    country: str = ""

class SiteInfo(BaseModel):
    site_id: str
    city: str
    country: str
    lat: float
    lon: float
    capabilities: list[str] = []

class LocationInfo(BaseModel):
    headquarters: Optional[Location] = None
    manufacturing_sites: list[SiteInfo] = Field(default_factory=list)
    shipping_regions: list[str] = Field(default_factory=list)

class ESGRating(BaseModel):
    provider: str
    score: float
    tier: str
    valid_until: Optional[str] = None

class Compliance(BaseModel):
    jurisdictions: list[str] = Field(default_factory=list)
    regulations: list[str] = Field(default_factory=list)
    sanctions_clear: bool = True
    esg_rating: Optional[ESGRating] = None

class InsuranceInfo(BaseModel):
    product_liability: bool = True
    max_coverage_eur: float = 0

class Policies(BaseModel):
    payment_terms: str = "Net 30"
    incoterms: list[str] = Field(default_factory=list)
    accepted_currencies: list[str] = Field(default_factory=lambda: ["EUR"])
    insurance: Optional[InsuranceInfo] = None
    min_contract_value_eur: float = 0
    nda_required: bool = False

class Trust(BaseModel):
    trust_score: float = 0.5
    years_in_operation: int = 0
    ferrari_tier_status: str = "pending"
    past_contracts: int = 0
    on_time_delivery_pct: float = 0
    defect_rate_ppm: float = 0
    dispute_count_12m: int = 0

class NetworkInfo(BaseModel):
    endpoint: str = ""
    protocol: str = "HTTP/JSON"
    api_version: str = "1.0"
    supported_message_types: list[str] = Field(default_factory=list)
    framework: str = "plain_python"
    heartbeat_url: str = ""

class UpstreamDependency(BaseModel):
    material: str
    typical_supplier_role: str
    critical: bool = False

class AgentFact(BaseModel):
    agent_id: str
    name: str
    role: str
    description: str = ""
    capabilities: Capabilities = Capabilities()
    identity: Optional[Identity] = None
    certifications: list[Certification] = Field(default_factory=list)
    location: Optional[LocationInfo] = None
    compliance: Optional[Compliance] = None
    policies: Optional[Policies] = None
    trust: Optional[Trust] = None
    network: Optional[NetworkInfo] = None
    upstream_dependencies: list[UpstreamDependency] = Field(default_factory=list)
    registered_at: str = ""
    last_heartbeat: str = ""
    status: str = "active"


# ── Message Schema (Agent-to-Agent) ─────────────────────────────────────────

class MessageMetadata(BaseModel):
    hop_count: int = 1
    origin: str = ""
    trace_path: list[str] = Field(default_factory=list)

class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: make_id("msg"))
    conversation_id: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    from_agent: str = Field(alias="from", default="")
    to_agent: str = Field(alias="to", default="")
    type: str = ""
    priority: str = "normal"
    payload: dict = Field(default_factory=dict)
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)

    class Config:
        populate_by_name = True


# ── Product Catalogue ───────────────────────────────────────────────────────

class CatalogueProduct(BaseModel):
    product_id: str
    name: str
    description: str = ""
    selling_price_eur: float
    intent_template: str = "Buy all parts required to assemble one {name}"
    currency: str = "EUR"


class PolicySpec(BaseModel):
    jurisdiction: str = "EU"
    max_risk_score: float = 0.7
    min_trust_score: float = 0.70
    min_esg_score: float = 50
    forbid_single_supplier: bool = False


class PolicyEvaluation(BaseModel):
    compliant: bool
    violations: list[dict] = Field(default_factory=list)
    explanations: list[str] = Field(default_factory=list)


class EscalationEvent(BaseModel):
    escalation_id: str = ""
    reason: str = ""
    agent_id: str | None = None
    trust_score: float | None = None
    risk_score: float | None = None
    threshold: float = 0.0
    timestamp: str = ""


class EscalationResponse(BaseModel):
    escalation_id: str
    action: str = "proceed"


class RiskReport(BaseModel):
    agent_id: str
    risk_type: str
    severity: float
    timestamp: str = ""


class InteractionRecord(BaseModel):
    agent_id: str
    event_type: str
    payload: dict = Field(default_factory=dict)
    timestamp: str = ""


class TrustSubmission(BaseModel):
    agent_id: str
    dimension: str
    score: float
    context: str = ""
    rater_id: str = ""


class ProfitSummary(BaseModel):
    total_revenue_eur: float
    total_cost_eur: float
    total_profit_eur: float
    profit_per_item_eur: float
    quantity: int
    margin_pct: float


# ── Trigger Request ─────────────────────────────────────────────────────────

class TriggerRequest(BaseModel):
    intent: str | None = None
    budget_eur: float = 500000
    product_id: str | None = None
    quantity: int = 1
    strategy: str = "cost-first"


# ── Frontend Data Shapes ────────────────────────────────────────────────────

class GraphNode(BaseModel):
    id: str
    label: str
    role: str
    color: str = "#2196F3"
    location: Optional[dict] = None
    trust_score: Optional[float] = None
    status: str = "active"
    size: int = 30

class GraphEdge(BaseModel):
    source: str = Field(alias="from")
    target: str = Field(alias="to")
    type: str = ""
    label: str = ""
    value_eur: Optional[float] = None
    message_count: int = 0
    status: str = ""

    class Config:
        populate_by_name = True

class LiveMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: make_id("msg"))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    from_id: str = ""
    from_label: str = ""
    to_id: str = ""
    to_label: str = ""
    type: str = ""
    summary: str = ""
    detail: str = ""
    color: str = "#2196F3"
    icon: str = "info"

class HeroMetric(BaseModel):
    label: str
    value: str
    trend: Optional[str] = None

class DashboardData(BaseModel):
    hero_metrics: list[HeroMetric] = Field(default_factory=list)
    cost_breakdown: list[dict] = Field(default_factory=list)
    timeline_items: list[dict] = Field(default_factory=list)
    supplier_markers: list[dict] = Field(default_factory=list)
    supplier_routes: list[dict] = Field(default_factory=list)
    risk_items: list[dict] = Field(default_factory=list)
    reasoning_log: list[dict] = Field(default_factory=list)
    negotiations: list[dict] = Field(default_factory=list)
    discovery_results: dict = Field(default_factory=dict)
    compliance_summary: dict = Field(default_factory=dict)
