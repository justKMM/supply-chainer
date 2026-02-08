"""
Coordination Cascade Orchestrator

Executes the full supply chain procurement cascade:
  Intent → BOM Decomposition → Discovery → Quotes → Negotiation →
  Compliance → Purchase Orders → Logistics → Report Generation
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from backend.config import BUDGET_CEILING_EUR, TRUST_THRESHOLD
from backend.schemas import LiveMessage, make_id
from backend.services.registry_service import registry
from backend.services.agent_service import ai_reason
from backend.services.risk_propagation_service import risk_propagation
from backend.services.event_engine import trigger_events, apply_quote_impacts, apply_logistics_impacts
from backend.services.cascade_steps.init import run_init
from backend.services.cascade_steps.intent import run_intent
from backend.services.cascade_steps.discovery import run_discovery
from backend.services.cascade_steps.quotes import run_quotes
from backend.services.cascade_steps.negotiation import run_negotiation
from backend.services.cascade_steps.compliance import run_compliance
from backend.services.cascade_steps.orders import run_orders
from backend.services.cascade_steps.logistics import run_logistics
from backend.services.cascade_steps.reputation import run_reputation
from backend.services.cascade_steps.reporting import run_reporting
from backend.services.pubsub_service import event_bus
from backend.services.trust_service import reputation_ledger
from backend.services.intelligence_service import generate_intelligence_signals


# ── State ────────────────────────────────────────────────────────────────────

cascade_state = {
    "running": False,
    "report": None,
    "progress": 0,
    "paused": False,
    "escalation": None,
    "escalation_event": None,
    "escalation_response": None,
}


def _emit_escalation(reason: str, agent_id: str | None, trust_score: float | None, risk_score: float | None, _emit) -> str:
    """Emit escalation event; return escalation_id."""
    esc_id = make_id("esc")
    cascade_state["paused"] = True
    cascade_state["escalation"] = {
        "escalation_id": esc_id,
        "reason": reason,
        "agent_id": agent_id,
        "trust_score": trust_score,
        "risk_score": risk_score,
        "threshold": TRUST_THRESHOLD,
    }
    cascade_state["escalation_event"] = asyncio.Event()
    _emit(
        "escalation",
        "Escalation",
        "ferrari-procurement-01",
        "Ferrari Procurement",
        "escalation",
        summary=None,
        payload={
            "summary": reason,
            "detail": "Trust/risk threshold exceeded. Awaiting human response.",
        },
    )
    return esc_id


def respond_to_escalation(escalation_id: str, action: str) -> bool:
    """Human responds to escalation; unblock cascade if applicable."""
    if cascade_state.get("escalation", {}).get("escalation_id") != escalation_id:
        return False
    cascade_state["escalation_response"] = action
    ev = cascade_state.get("escalation_event")
    if ev:
        ev.set()
    cascade_state["paused"] = False
    return True


def prepare_new_cascade():
    """Clear all stateful services and escalation state before a new cascade."""
    registry.clear()
    event_bus.clear()
    reputation_ledger.clear()
    risk_propagation.clear()
    cascade_state["paused"] = False
    cascade_state["escalation"] = None
    cascade_state["escalation_response"] = None


def _ts(offset_seconds: int = 0) -> str:
    return (datetime.utcnow() + timedelta(seconds=offset_seconds)).isoformat() + "Z"


def _emit(
    from_id,
    from_label,
    to_id,
    to_label,
    msg_type,
    summary=None,
    detail="",
    color="#2196F3",
    icon="info",
    payload=None,
):
    if summary is None:
        from backend.services.message_builder import build_message_content
        summary, detail, color, icon = build_message_content(msg_type, payload or {})
    msg = LiveMessage(
        message_id=make_id("msg"),
        timestamp=_ts(),
        from_id=from_id,
        from_label=from_label,
        to_id=to_id,
        to_label=to_label,
        type=msg_type,
        summary=summary or "",
        detail=detail or "",
        color=color,
        icon=icon,
    )
    registry.log_message(msg)
    return msg


# ── Main Cascade ─────────────────────────────────────────────────────────────

async def run_cascade(
    intent: str,
    budget_eur: float = BUDGET_CEILING_EUR,
    catalogue_product=None,
    quantity: int = 1,
    strategy: str = "cost-first",
) -> dict:
    """Modular orchestrator for the full procurement cascade."""
    cascade_state["running"] = True
    cascade_state["progress"] = 0
    cascade_state["report"] = None

    report = {
        "report_id": make_id("NCR-FERRARI"),
        "intent": intent,
        "initiated_by": "ferrari-procurement-01",
        "initiated_at": _ts(),
        "status": "in_progress",
        "bill_of_materials_summary": {},
        "discovery_results": {"agents_discovered": 0, "agents_qualified": 0, "agents_disqualified": 0, "disqualification_reasons": [], "discovery_paths": []},
        "negotiations": [],
        "compliance_summary": {"total_checks": 0, "passed": 0, "flagged": 0, "failed": 0, "flags": []},
        "logistics_plan": {"total_shipments": 0, "total_logistics_cost_eur": 0, "shipments": [], "critical_path_days": 0, "bottleneck": ""},
        "execution_plan": {"total_cost_eur": 0, "cost_breakdown": {"components_eur": 0, "logistics_eur": 0, "insurance_eur": 0, "compliance_fees_eur": 0}, "timeline": {}, "suppliers_engaged": 0, "purchase_orders_issued": 0, "risk_assessment": {"overall_risk": "low", "risks": []}},
        "disruptions_handled": [],
        "message_log_summary": {"total_messages": 0, "by_type": {}},
        "reasoning_log": [],
        "graph_nodes": [],
        "graph_edges": [],
        "dashboard": {},
        "pubsub_summary": {},
        "reputation_summary": {},
        "intelligence_feed": [],
        "profit_summary": None,
        "policy_evaluation": None,
        "intent_expansion": None,
        "event_log": [],
    }

    try:
        await run_init(_emit)
        cascade_state["progress"] = 5

        bom = await run_intent(intent, report, _emit, _ts)
        cascade_state["progress"] = 15

        qualified_agents, _ = await run_discovery(bom, report, _emit, _ts)
        cascade_state["progress"] = 30

        quotes = await run_quotes(qualified_agents, report, _emit, _ts)
        cascade_state["progress"] = 45

        pre_events = trigger_events("pre_quotes")
        report["event_log"].extend(pre_events)
        apply_quote_impacts(quotes, pre_events)

        for ev in pre_events:
            reasoning = await ai_reason(
                "Ferrari Procurement AI",
                "procurement_agent",
                f"Event occurred: {ev['type']} with impact {ev['impact']}. Adjust approach?",
            )
            report["reasoning_log"].append({"agent": "Ferrari Procurement", "timestamp": _ts(), "thought": reasoning})
            _emit(
                "event-engine",
                "Event Engine",
                "ferrari-procurement-01",
                "Ferrari Procurement",
                "disruption_alert",
                summary=None,
                payload={"summary": f"Event: {ev['type']}", "detail": str(ev["impact"])},
            )

        final_orders = await run_negotiation(quotes, report, _emit, _ts, strategy)
        cascade_state["progress"] = 60

        await run_compliance(final_orders, report, _emit)
        cascade_state["progress"] = 72

        total_component_cost, po_count = await run_orders(final_orders, _emit)
        cascade_state["progress"] = 82

        logistics_plan, max_lead_days = run_logistics(final_orders, _emit)
        report["logistics_plan"] = logistics_plan
        cascade_state["progress"] = 90

        post_events = trigger_events("post_logistics")
        report["event_log"].extend(post_events)
        apply_logistics_impacts(logistics_plan, post_events)

        report["reputation_summary"] = run_reputation(final_orders, _emit)
        cascade_state["progress"] = 94

        intel_results = await generate_intelligence_signals(event_bus, count=5)
        report["intelligence_feed"] = intel_results
        report["pubsub_summary"] = event_bus.get_summary()
        cascade_state["progress"] = 96

        run_reporting(
            report,
            qualified_agents,
            final_orders,
            total_component_cost,
            po_count,
            logistics_plan,
            max_lead_days,
            catalogue_product,
            quantity,
            _emit,
            _ts,
        )

        messages = registry.get_messages()
        by_type = {}
        for m in messages:
            by_type[m.type] = by_type.get(m.type, 0) + 1
        report["message_log_summary"] = {"total_messages": len(messages), "by_type": by_type}

    except Exception as e:
        report["status"] = "error"
        report["error"] = str(e)
        _emit(
            "system",
            "System",
            "system",
            "System",
            "error",
            summary=None,
            payload={"summary": f"Cascade error: {str(e)}"},
        )

    cascade_state["running"] = False
    cascade_state["progress"] = 100
    cascade_state["report"] = report
    return report


def simulate_supplier_failure(agent_id: str) -> dict | None:
    """Simulate 'what if supplier fails?' — returns cost/delay delta and alternate supplier."""
    report = cascade_state.get("report")
    if not report or report.get("status") != "completed":
        return None

    paths = report.get("discovery_results", {}).get("discovery_paths", [])
    failed_path = next((p for p in paths if p.get("selected") == agent_id), None)
    if not failed_path:
        return {"error": "Agent not in current plan", "agent_id": agent_id}

    need = failed_path.get("need", "")
    query = failed_path.get("query", "role=tier_1_supplier")
    cat = need.split()[0].lower() if need else ""
    if "capability=" in query:
        cat = query.split("capability=")[-1].split(",")[0].strip()

    candidates = registry.search(role="tier_1_supplier", capability=cat or "braking_system", min_trust=0.0, include_deprecated=True)
    candidates = [c for c in candidates if c.agent_id != agent_id]

    if not candidates:
        return {
            "agent_id": agent_id,
            "category": cat,
            "alternate_supplier": None,
            "original_cost": report.get("execution_plan", {}).get("total_cost_eur", 0),
            "new_cost": None,
            "cost_delta": None,
            "original_days": 0,
            "new_days": None,
            "delay_delta": None,
            "message": "No alternate supplier found",
        }

    best = max(candidates, key=lambda a: a.trust.trust_score if a.trust else 0)
    products = best.capabilities.products
    unit_price = products[0].unit_price_eur if products else 0
    lead_days = products[0].lead_time_days if products else 14

    exec_plan = report.get("execution_plan", {})
    original_cost = exec_plan.get("total_cost_eur", 0)
    original_days = 30
    timeline = exec_plan.get("timeline", {})
    if "assembly_ready" in timeline:
        try:
            start = datetime.fromisoformat(timeline.get("procurement_start", "")[:10])
            end = datetime.fromisoformat(timeline.get("assembly_ready", "")[:10])
            original_days = (end - start).days
        except Exception:
            pass

    cost_per_cat = original_cost / max(len(paths), 1)
    new_cost = original_cost - cost_per_cat + (unit_price * 2)
    cost_delta = new_cost - original_cost
    new_days = max(original_days, lead_days + 5)
    delay_delta = max(0, new_days - original_days)

    return {
        "agent_id": agent_id,
        "category": cat,
        "alternate_supplier": {"agent_id": best.agent_id, "name": best.name, "unit_price_eur": unit_price, "lead_time_days": lead_days},
        "original_cost": round(original_cost, 2),
        "new_cost": round(new_cost, 2),
        "cost_delta": round(cost_delta, 2),
        "original_days": original_days,
        "new_days": new_days,
        "delay_delta": delay_delta,
    }
