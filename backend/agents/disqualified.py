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
    Product,
    Trust,
)


def disqualified_agents() -> list[AgentFact]:
    agents: list[AgentFact] = []

    # Disqualified agents (for realism)
    agents.append(AgentFact(
        agent_id="cheapparts-cn-03",
        name="CheapParts Shenzhen Ltd.",
        role="tier_1_supplier",
        description="Low-cost brake component manufacturer.",
        capabilities=Capabilities(
            products=[
                Product(product_id="generic-brake-disc", name="Steel Brake Disc 380mm", category="braking_system",
                        unit_price_eur=180.00, min_order_quantity=500, lead_time_days=30),
            ],
        ),
        identity=Identity(legal_entity="CheapParts Ltd.", registration_country="CN"),
        certifications=[
            Certification(type="ISO_9001", description="Quality Management", issued_by="Local", valid_until="2025-01-01", status="expired"),
        ],
        location=LocationInfo(headquarters=Location(lat=22.5431, lon=114.0579, city="Shenzhen", country="CN")),
        compliance=Compliance(jurisdictions=["CN"], regulations=[], sanctions_clear=True,
                              esg_rating=ESGRating(provider="Self-assessed", score=35, tier="None")),
        trust=Trust(trust_score=0.31, years_in_operation=4, ferrari_tier_status="not_approved", past_contracts=12, on_time_delivery_pct=72.0, defect_rate_ppm=340, dispute_count_12m=5),
    ))

    agents.append(AgentFact(
        agent_id="noname-logistics-07",
        name="NoName Freight Co.",
        role="logistics_provider",
        description="Small regional freight company.",
        capabilities=Capabilities(services=["road_freight"]),
        identity=Identity(legal_entity="NoName Freight", registration_country="RO"),
        location=LocationInfo(headquarters=Location(lat=44.4268, lon=26.1025, city="Bucharest", country="RO")),
        trust=Trust(trust_score=0.31, years_in_operation=2, ferrari_tier_status="not_approved", past_contracts=8, on_time_delivery_pct=68.0),
    ))

    return agents
