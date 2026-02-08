from __future__ import annotations

from backend.schemas import (
    AgentFact,
    Capabilities,
    Compliance,
    Identity,
    Location,
    LocationInfo,
    NetworkInfo,
    Trust,
)


def compliance_agents() -> list[AgentFact]:
    agents: list[AgentFact] = []

    # Compliance Agent
    agents.append(AgentFact(
        agent_id="eu-compliance-agent-01",
        name="EU Compliance Validator",
        role="compliance_agent",
        description="Automated compliance validation service. Checks certifications, sanctions, ESG scores, and regulatory compliance for all supply chain actors.",
        capabilities=Capabilities(
            services=["certification_validity", "sanctions_screening", "esg_threshold", "regulation_compliance"],
        ),
        identity=Identity(legal_entity="SupplyGuard GmbH", registration_country="DE"),
        location=LocationInfo(
            headquarters=Location(lat=50.1109, lon=8.6821, city="Frankfurt", country="DE"),
        ),
        compliance=Compliance(jurisdictions=["EU"], regulations=["EU_REACH", "EU_ELV_Directive", "CE_Marking", "EU_RoHS"]),
        trust=Trust(trust_score=0.95, years_in_operation=12, ferrari_tier_status="approved_provider", past_contracts=5400),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/eu-compliance-agent-01",
                            supported_message_types=["compliance_check", "compliance_result"]),
    ))

    return agents
