from __future__ import annotations

from backend.schemas import (
    AgentFact,
    Capabilities,
    Certification,
    Compliance,
    ESGRating,
    Identity,
    Location,
    LocationInfo,
    NetworkInfo,
    Policies,
    Product,
    ProductionCapacity,
    SiteInfo,
    Trust,
)


def core_agents() -> list[AgentFact]:
    agents: list[AgentFact] = []

    # Ferrari Procurement Agent
    agents.append(AgentFact(
        agent_id="ferrari-procurement-01",
        name="Ferrari Procurement AI",
        role="procurement_agent",
        description="Central procurement intelligence for Ferrari S.p.A. Decomposes purchase intents, discovers suppliers, negotiates contracts, and orchestrates the full supply cascade.",
        capabilities=Capabilities(
            services=["intent_decomposition", "supplier_discovery", "negotiation", "order_management"],
        ),
        identity=Identity(legal_entity="Ferrari S.p.A.", registration_country="IT", vat_id="IT00159560366"),
        location=LocationInfo(
            headquarters=Location(lat=44.5294, lon=10.8633, city="Maranello", country="IT"),
        ),
        trust=Trust(trust_score=1.0, years_in_operation=78, ferrari_tier_status="internal", past_contracts=0),
        network=NetworkInfo(
            endpoint="http://localhost:8000/agent/ferrari-procurement-01",
            supported_message_types=["request_quote", "negotiate", "purchase_order", "disruption_alert"],
        ),
    ))

    # Ferrari Powertrain (Internal) — Engine/Powertrain
    agents.append(AgentFact(
        agent_id="ferrari-powertrain-internal-01",
        name="Ferrari Powertrain Division",
        role="tier_1_supplier",
        description="In-house powertrain engineering and production at Maranello. Produces the F163 hybrid V6 engine.",
        capabilities=Capabilities(
            products=[
                Product(product_id="f163-v6-engine", name="F163 2.9L Twin-Turbo V6 Engine",
                        category="powertrain", subcategory="engine",
                        specifications={"displacement_cc": 2992, "power_hp": 663, "torque_nm": 740, "hybrid": True},
                        unit_price_eur=45000.00, min_order_quantity=1, lead_time_days=10),
                Product(product_id="dct-8speed-gearbox", name="8-Speed Dual-Clutch Transmission",
                        category="powertrain", subcategory="gearbox",
                        specifications={"type": "DCT", "gears": 8, "max_torque_nm": 900},
                        unit_price_eur=18000.00, min_order_quantity=1, lead_time_days=8),
            ],
            services=["engine_assembly", "dyno_testing", "calibration"],
            production_capacity=ProductionCapacity(units_per_month=800, current_utilization_pct=78),
        ),
        identity=Identity(legal_entity="Ferrari S.p.A.", registration_country="IT", vat_id="IT00159560366"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="DNV GL", valid_until="2027-01-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=44.5294, lon=10.8633, city="Maranello", country="IT"),
            manufacturing_sites=[SiteInfo(site_id="maranello-engine", city="Maranello", country="IT", lat=44.5294, lon=10.8633, capabilities=["engine_assembly", "dyno_testing", "machining"])],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "Euro_6d", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="MSCI", score=78, tier="AA", valid_until="2026-06-01")),
        policies=Policies(payment_terms="Internal", incoterms=["EXW"]),
        trust=Trust(trust_score=1.0, years_in_operation=78, ferrari_tier_status="internal", past_contracts=0, on_time_delivery_pct=99.1, defect_rate_ppm=3),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/ferrari-powertrain-internal-01",
                            supported_message_types=["request_quote", "purchase_order"]),
    ))

    # Assembly Coordinator
    agents.append(AgentFact(
        agent_id="maranello-assembly-01",
        name="Maranello Assembly Coordinator",
        role="assembly_coordinator",
        description="Manages BOM validation, assembly sequencing, and delivery scheduling at the Maranello plant.",
        capabilities=Capabilities(
            services=["bom_management", "assembly_sequencing", "delivery_scheduling", "quality_control"],
        ),
        identity=Identity(legal_entity="Ferrari S.p.A.", registration_country="IT"),
        location=LocationInfo(
            headquarters=Location(lat=44.5294, lon=10.8633, city="Maranello", country="IT"),
        ),
        trust=Trust(trust_score=1.0, years_in_operation=78, ferrari_tier_status="internal"),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/maranello-assembly-01",
                            supported_message_types=["purchase_order", "order_confirmation", "shipment_update"]),
    ))

    return agents
