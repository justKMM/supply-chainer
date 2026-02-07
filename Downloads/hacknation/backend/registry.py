"""In-memory Agent Registry — the DNS of the supply chain agent network."""

from __future__ import annotations
import asyncio
from datetime import datetime
from typing import Optional
from backend.schemas import AgentFact, LiveMessage


class AgentRegistry:
    """Lightweight in-memory registry supporting register / search / list / deregister."""

    def __init__(self):
        self._agents: dict[str, AgentFact] = {}
        self._messages: list[LiveMessage] = []
        self._subscribers: list[asyncio.Queue] = []

    # ── Registration ─────────────────────────────────────────────────────

    def register(self, agent: AgentFact) -> AgentFact:
        agent.registered_at = datetime.utcnow().isoformat() + "Z"
        agent.last_heartbeat = agent.registered_at
        agent.status = "active"
        self._agents[agent.agent_id] = agent
        return agent

    def deregister(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    # ── Lookup ───────────────────────────────────────────────────────────

    def get(self, agent_id: str) -> Optional[AgentFact]:
        return self._agents.get(agent_id)

    def list_all(self) -> list[AgentFact]:
        return list(self._agents.values())

    def search(
        self,
        role: Optional[str] = None,
        capability: Optional[str] = None,
        region: Optional[str] = None,
        certification: Optional[str] = None,
        min_trust: float = 0.0,
    ) -> list[AgentFact]:
        results = list(self._agents.values())

        if role:
            results = [a for a in results if a.role == role]

        if capability:
            results = [
                a for a in results
                if any(p.category == capability for p in a.capabilities.products)
            ]

        if region:
            results = [
                a for a in results
                if a.location and a.location.headquarters and a.location.headquarters.country
                and (
                    a.location.headquarters.country == region
                    or region in (a.location.shipping_regions if a.location else [])
                )
            ]

        if certification:
            results = [
                a for a in results
                if any(c.type == certification for c in a.certifications)
            ]

        if min_trust > 0:
            results = [
                a for a in results
                if a.trust and a.trust.trust_score >= min_trust
            ]

        return results

    # ── Message logging & SSE ────────────────────────────────────────────

    def log_message(self, msg: LiveMessage):
        self._messages.append(msg)
        for q in self._subscribers:
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                pass

    def get_messages(self) -> list[LiveMessage]:
        return list(self._messages)

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=500)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    def clear(self):
        self._agents.clear()
        self._messages.clear()


# Global singleton
registry = AgentRegistry()
