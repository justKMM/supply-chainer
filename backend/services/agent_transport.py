"""HTTP transport for protocol-level agent messaging."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Optional

import requests

from backend.config import AGENT_PROTOCOL_SECRET
from backend.schemas import AgentProtocolMessage, AgentProtocolReceipt, LiveMessage
from backend.services.registry_service import registry
from backend.adapters.a2a_adapter import send_a2a


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
    # Route by agent advertized protocol (default HTTP/JSON)
    protocol = (agent.network.protocol if agent and agent.network and agent.network.protocol else "HTTP/JSON").upper()
    if protocol in ("HTTP/JSON", "HTTP"):
        return send_protocol_message(message, endpoint)

    if protocol == "MCP":
        # Minimal in-process Message Channel (MCP) delivery: log the message
        try:
            lm = LiveMessage(
                message_id=message.message_id,
                from_id=message.from_agent,
                from_label=message.from_agent,
                to_id=message.to_agent,
                to_label=message.to_agent,
                type=message.message_type or message.message_type,
                summary=(str(message.payload)[:120] if message.payload else ""),
                detail="Delivered via MCP",
            )
            registry.log_message(lm)
            return AgentProtocolReceipt(
                message_id=message.message_id,
                from_agent=message.from_agent,
                to_agent=message.to_agent,
                status="accepted",
                detail="Delivered via MCP",
            )
        except Exception as exc:
            return AgentProtocolReceipt(
                message_id=message.message_id,
                from_agent=message.from_agent,
                to_agent=message.to_agent,
                status="error",
                detail=f"MCP delivery failed: {exc}",
            )

    if protocol == "A2A":
        # Use A2A adapter to send (falls back to registry log if no endpoint)
        if not endpoint:
            # fall back to MCP-like logging when no endpoint provided
            lm = LiveMessage(
                message_id=message.message_id,
                from_id=message.from_agent,
                from_label=message.from_agent,
                to_id=message.to_agent,
                to_label=message.to_agent,
                type=message.message_type or message.message_type,
                summary=(str(message.payload)[:120] if message.payload else ""),
                detail="A2A (no endpoint) logged via MCP fallback",
            )
            registry.log_message(lm)
            return AgentProtocolReceipt(
                message_id=message.message_id,
                from_agent=message.from_agent,
                to_agent=message.to_agent,
                status="accepted",
                detail="A2A logged via MCP fallback",
            )
        try:
            payload = _attach_signature(message)
            result = send_a2a(endpoint, payload)
            if result.get("ok"):
                # try to use returned json as receipt
                if result.get("json") and isinstance(result["json"], dict):
                    try:
                        return AgentProtocolReceipt(**result["json"])
                    except Exception:
                        pass
                return AgentProtocolReceipt(
                    message_id=message.message_id,
                    from_agent=message.from_agent,
                    to_agent=message.to_agent,
                    status="accepted",
                    detail="A2A delivered",
                )
            return AgentProtocolReceipt(
                message_id=message.message_id,
                from_agent=message.from_agent,
                to_agent=message.to_agent,
                status="rejected",
                detail=f"A2A HTTP {result.get('status_code')}",
            )
        except Exception as exc:
            return AgentProtocolReceipt(
                message_id=message.message_id,
                from_agent=message.from_agent,
                to_agent=message.to_agent,
                status="error",
                detail=f"A2A send error: {exc}",
            )

    # Unknown protocol — fall back to HTTP behavior
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
