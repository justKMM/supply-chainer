"""
AI-powered supply chain agents with OpenAI reasoning.

Each agent is an independent actor that can:
- Reason about decisions using OpenAI
- Communicate via the message schema
- Be discovered through the registry
"""

from __future__ import annotations

import copy
import json

from backend.adapters.openai_client import get_async_client
from backend.config import OPENAI_MODEL
from backend.agents import (
    CATEGORY_AGENT_MAP,
    compliance_agents,
    core_agents,
    disqualified_agents,
    logistics_agents,
    supplier_agents,
)
from backend.schemas import AgentFact

client = get_async_client()


# ── OpenAI reasoning helper ─────────────────────────────────────────────────


async def ai_reason(agent_name: str, role: str, prompt: str) -> str:
    """Ask OpenAI to reason as a specific supply-chain agent."""
    try:
        resp = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are {agent_name}, a {role} in Ferrari's supply chain network. "
                        "You make realistic business decisions. Be concise (2-3 sentences). "
                        "Respond with business reasoning only, no markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=10000,
            # temperature=0.7,
        )
        print(
            f"Agent {agent_name} with role {role} has prompt {prompt} and answer {resp.choices[0].message.content}"
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Reasoning unavailable: {e}]"


async def ai_expand_intent(intent: str) -> dict:
    """Expand high-level intent into component, logistics, and compliance sub-intents."""
    try:
        resp = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an intent resolver for Ferrari supply chain. Given a procurement intent, "
                        "return ONLY valid JSON object with keys: component_intents, logistics_intents, compliance_intents. "
                        'component_intents: array of component sourcing intents (e.g. "Source EU-compliant brake systems"). '
                        'logistics_intents: array of logistics intents (e.g. "Coordinate EU road freight to Maranello"). '
                        'compliance_intents: array of compliance intents (e.g. "Validate IATF_16949 certification"). '
                        "Each array should have 1-3 items."
                    ),
                },
                {"role": "user", "content": intent},
            ],
            max_completion_tokens=10000,
            # temperature=0.3,
        )
        text = resp.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        return json.loads(text)
    except Exception:
        return {
            "component_intents": [f"Source components for {intent[:80]}"],
            "logistics_intents": ["Coordinate EU road freight to Maranello"],
            "compliance_intents": ["Validate IATF_16949 and EU_REACH compliance"],
        }


async def ai_decompose_bom(intent: str) -> list[dict]:
    """Use OpenAI to decompose an intent into a Bill of Materials."""
    try:
        resp = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Ferrari production engineer. Given a procurement intent, "
                        "decompose it into component categories needed. Return ONLY valid JSON array. "
                        'Each item: {"category": str, "parts_count": int, '
                        '"key_components": [str, str, str]}. '
                        "Include: powertrain, braking_system, body_chassis, electronics, "
                        "interior, suspension, wheels_tires, exhaust_emissions."
                    ),
                },
                {"role": "user", "content": intent},
            ],
            max_completion_tokens=10000,
            # temperature=0.3,
        )
        text = resp.choices[0].message.content.strip()
        return _parse_json_array(text)
    except (json.JSONDecodeError, KeyError, IndexError):
        return _default_bom()
    except Exception:
        return _default_bom()


DEFAULT_BOM: list[dict] = [
    {
        "category": "powertrain",
        "parts_count": 12,
        "key_components": [
            "V6 Engine Block",
            "Turbocharger Assembly",
            "8-Speed DCT Gearbox",
        ],
    },
    {
        "category": "braking_system",
        "parts_count": 6,
        "key_components": [
            "Carbon Ceramic Disc 396mm",
            "Brake Caliper Set",
            "Brake Fluid Reservoir",
        ],
    },
    {
        "category": "body_chassis",
        "parts_count": 8,
        "key_components": [
            "Carbon Fiber Monocoque",
            "Aluminum Subframe",
            "Body Panels",
        ],
    },
    {
        "category": "electronics",
        "parts_count": 9,
        "key_components": ["ECU", "Infotainment Unit", "Sensor Array"],
    },
    {
        "category": "interior",
        "parts_count": 5,
        "key_components": [
            "Leather Seat Assembly",
            "Steering Wheel",
            "Dashboard Module",
        ],
    },
    {
        "category": "suspension",
        "parts_count": 4,
        "key_components": ["MagneRide Dampers", "Control Arms", "Anti-Roll Bar"],
    },
    {
        "category": "wheels_tires",
        "parts_count": 2,
        "key_components": ['Forged Alloy Wheels 20"', "Pirelli P Zero Tires"],
    },
    {
        "category": "exhaust_emissions",
        "parts_count": 1,
        "key_components": ["Catalytic Converter + Exhaust System"],
    },
]


def _parse_json_array(text: str) -> list[dict]:
    """Extract and parse a JSON array from model output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1].strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    return json.loads(cleaned)


def _default_bom() -> list[dict]:
    return copy.deepcopy(DEFAULT_BOM)


# ── Seed Data: Pre-built AgentFacts for all supply chain actors ─────────────


def create_seed_agents() -> list[AgentFact]:
    """Create realistic supplier agents for the Ferrari supply chain."""
    return (
        core_agents()
        + supplier_agents()
        + logistics_agents()
        + compliance_agents()
        + disqualified_agents()
    )
