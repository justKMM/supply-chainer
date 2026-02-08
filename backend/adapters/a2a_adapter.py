from __future__ import annotations

import requests
from typing import Any

from backend.schemas import AgentProtocolMessage


def send_a2a(endpoint: str, payload: dict, timeout: float = 2.0) -> dict[str, Any]:
    """Send a message over an A2A endpoint.

    This adapter is intentionally lightweight: it posts JSON to the configured
    endpoint and returns a small result dict to let callers build receipts.
    """
    if not endpoint:
        raise ValueError("No A2A endpoint configured")

    headers = {
        "Content-Type": "application/json",
        "X-A2A-Transport": "1",
    }
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    result: dict[str, Any] = {"ok": resp.ok, "status_code": resp.status_code}
    try:
        result["json"] = resp.json() if resp.content else None
    except Exception:
        result["json"] = None
    return result
