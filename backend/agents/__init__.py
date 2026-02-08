"""Agent seed data grouped by domain."""

from backend.agents.category_map import CATEGORY_AGENT_MAP
from backend.agents.compliance import compliance_agents
from backend.agents.core import core_agents
from backend.agents.disqualified import disqualified_agents
from backend.agents.logistics import logistics_agents
from backend.agents.suppliers import supplier_agents

__all__ = [
    "CATEGORY_AGENT_MAP",
    "compliance_agents",
    "core_agents",
    "disqualified_agents",
    "logistics_agents",
    "supplier_agents",
]
