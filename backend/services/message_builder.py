"""Dynamic message builder — derive summaries from payload data."""

from __future__ import annotations

import json


def _fallback(payload: dict | None) -> tuple[str, str]:
    if not payload:
        return "Event update", ""
    try:
        return "Event update", json.dumps(payload)[:500]
    except Exception:
        return "Event update", ""


def build_message_content(msg_type: str, payload: dict | None) -> tuple[str, str, str, str]:
    """Return summary, detail, color, icon for a message type."""
    payload = payload or {}
    summary = ""
    detail = ""
    color = "#2196F3"
    icon = "info"

    if msg_type == "request_quote":
        qty = payload.get("quantity")
        name = payload.get("product_name")
        budget = payload.get("budget_ceiling_eur")
        summary = f"Requesting quote for {qty}x {name}" if qty and name else "Requesting quote"
        detail = f"Budget ceiling: EUR {budget:,.0f}" if budget else ""
        color = "#4CAF50"
        icon = "request"
    elif msg_type == "quote_response":
        unit = payload.get("unit_price_eur")
        lead = payload.get("lead_time_days")
        summary = f"Quoted EUR {unit:,.0f}/unit, {lead}-day lead time" if unit and lead else "Quote response"
        detail = payload.get("quote_id", "")
        color = "#4CAF50"
        icon = "response"
    elif msg_type == "negotiate":
        offer = payload.get("offer_price_eur")
        summary = f"Counter offer: EUR {offer:,.0f}/unit" if offer else "Counter offer"
        detail = payload.get("reason", "")
        color = "#FF9800"
        icon = "negotiate"
    elif msg_type == "negotiate_response":
        counter = payload.get("counter_price_eur")
        summary = f"Counter: EUR {counter:,.0f}/unit" if counter else "Counter response"
        detail = payload.get("reason", "")
        color = "#FF9800"
        icon = "negotiate"
    elif msg_type == "purchase_order":
        qty = payload.get("quantity")
        name = payload.get("product_name")
        price = payload.get("unit_price_eur")
        summary = f"PO issued: {qty}x {name} @ EUR {price:,.0f}" if qty and name and price else "Purchase order issued"
        detail = payload.get("po_number", "")
        color = "#DC143C"
        icon = "order"
    elif msg_type == "order_confirmation":
        ship = payload.get("ship_date")
        deliver = payload.get("delivery_date")
        summary = f"Order confirmed. Ship: {ship}, Deliver: {deliver}" if ship and deliver else "Order confirmed"
        detail = payload.get("po_number", "")
        color = "#4CAF50"
        icon = "truck"
    elif msg_type == "compliance_check":
        agent = payload.get("agent_name")
        summary = f"Requesting compliance check for {agent}" if agent else "Compliance check requested"
        detail = payload.get("checks", "")
        color = "#FF9800"
        icon = "shield"
    elif msg_type == "compliance_result":
        status = payload.get("status")
        agent = payload.get("agent_name")
        summary = f"{agent}: {status}" if agent and status else "Compliance result"
        detail = payload.get("detail", "")
        color = "#4CAF50" if status == "approved" else "#F44336"
        icon = "check" if status == "approved" else "warning"
    elif msg_type == "logistics_request":
        summary = "Logistics request"
        detail = payload.get("route", "")
        color = "#9C27B0"
        icon = "truck"
    elif msg_type == "logistics_proposal":
        cost = payload.get("cost_eur")
        summary = f"Logistics proposal: EUR {cost:,.0f}" if cost else "Logistics proposal"
        detail = payload.get("route", "")
        color = "#9C27B0"
        icon = "truck"
    elif msg_type == "disruption_alert":
        summary = payload.get("summary", "Disruption alert")
        detail = payload.get("detail", "")
        color = "#F44336"
        icon = "alert"
    elif msg_type == "policy_violation":
        summary = payload.get("summary", "Policy violation")
        detail = payload.get("detail", "")
        color = "#FF9800"
        icon = "shield"
    elif msg_type == "escalation":
        summary = payload.get("summary", "Escalation required")
        detail = payload.get("detail", "")
        color = "#FF9800"
        icon = "warning"
    else:
        summary, detail = _fallback(payload)

    return summary, detail, color, icon
