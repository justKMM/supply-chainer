"""HTTP transport for protocol-level agent messaging."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Optional

import requests

from backend.config import AGENT_PROTOCOL_SECRET
from backend.schemas import AgentProtocolMessage, AgentProtocolReceipt
from backend.services.registry_service import registry


def _sign_payload(payload: dict, secret: str) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()


def _attach_signature(message: AgentProtocolMessage) -> dict:
    payload = message.dict()
    if AGENT_PROTOCOL_SECRET:
        payload.pop("signature", None)
        payload["signature"] = _sign_payload(payload, AGENT_PROTOCOL_SECRET)
    return payload


def send_protocol_message(message: AgentProtocolMessage, endpoint: str) -> AgentProtocolReceipt:
    if not endpoint:
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="skipped",
            detail="No endpoint configured",
        )

    try:
        resp = requests.post(endpoint, json=_attach_signature(message), timeout=2)
        if resp.ok:
            try:
                return AgentProtocolReceipt(**resp.json())
            except Exception:
                return AgentProtocolReceipt(
                    message_id=message.message_id,
                    from_agent=message.from_agent,
                    to_agent=message.to_agent,
                    status="accepted",
                    detail="Received (receipt parse fallback)",
                )
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="rejected",
            detail=f"HTTP {resp.status_code}",
        )
    except Exception as exc:
        return AgentProtocolReceipt(
            message_id=message.message_id,
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            status="error",
            detail=str(exc),
        )


def send_to_agent(message: AgentProtocolMessage) -> AgentProtocolReceipt:
    agent = registry.get(message.to_agent)
    endpoint = ""
    if agent and agent.network:
        endpoint = agent.network.endpoint
    return send_protocol_message(message, endpoint)


def verify_signature(message: AgentProtocolMessage) -> Optional[str]:
    """Return error string if invalid, otherwise None."""
    if not AGENT_PROTOCOL_SECRET:
        return None
    payload = message.dict()
    signature = payload.pop("signature", None)
    expected = _sign_payload(payload, AGENT_PROTOCOL_SECRET)
    if not signature or signature != expected:
        return "Invalid signature"
    return None
