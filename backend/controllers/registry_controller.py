from __future__ import annotations

import asyncio

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from backend.schemas import AgentFact, TriggerRequest, LiveMessage, make_id
from backend.services.cascade_service import run_cascade, cascade_state, prepare_new_cascade, simulate_supplier_failure
from backend.services.registry_service import registry
from backend.services.catalogue_service import catalogue_service
from backend.config import BUDGET_CEILING_EUR

router = APIRouter()


# ── Registry Endpoints ───────────────────────────────────────────────────────

@router.post("/registry/register", status_code=201)
async def register_agent(agent: AgentFact):
    return registry.register(agent)


@router.get("/registry/search")
async def search_agents(
    role: str | None = Query(None),
    capability: str | None = Query(None),
    region: str | None = Query(None),
    certification: str | None = Query(None),
    min_trust: float | None = Query(None),
    include_deprecated: bool = Query(False),
):
    results = registry.search(
        role=role,
        capability=capability,
        region=region,
        certification=certification,
        min_trust=min_trust,
        include_deprecated=include_deprecated,
    )
    return results


@router.get("/registry/list")
async def list_agents():
    return registry.list_all()


@router.get("/api/suppliers")
async def list_suppliers(role: str | None = Query(None)):
    """List all supplier agents (optionally filter by role)."""
    return registry.list_suppliers(role=role)


@router.get("/api/agents")
async def list_agents_protocol():
    """Protocol-ready agent discovery list."""
    return registry.list_protocol_agents()


@router.get("/registry/agent/{agent_id}")
async def get_agent(agent_id: str):
    agent = registry.get(agent_id)
    if not agent:
        return JSONResponse(status_code=404, content={"error": "Agent not found"})
    return agent


@router.get("/registry/health")
async def registry_health():
    """Return registry filter summary (min_trust, deprecated_agents, regions)."""
    return registry.get_health_filters()


@router.delete("/registry/deregister/{agent_id}", status_code=204)
async def deregister_agent(agent_id: str):
    registry.deregister(agent_id)


@router.post("/registry/log", status_code=201)
async def log_message(msg: LiveMessage):
    registry.log_message(msg)
    return {"status": "logged"}


@router.get("/registry/logs")
async def get_logs():
    return registry.get_messages()


# ── Cascade Trigger ──────────────────────────────────────────────────────────

@router.post("/registry/trigger")
async def trigger_cascade(req: TriggerRequest):
    if cascade_state["running"]:
        return JSONResponse(status_code=409, content={"error": "Cascade already running"})

    # Resolve intent: product_id+quantity or explicit intent
    intent = req.intent
    product = None
    quantity = req.quantity
    budget_eur = req.budget_eur

    if req.product_id and req.quantity > 0:
        product = catalogue_service.get(req.product_id)
        if not product:
            return JSONResponse(status_code=404, content={"error": "Product not found"})
        intent = catalogue_service.get_intent_for_product(product, req.quantity)
        quantity = req.quantity
        # Optionally derive budget from selling price (1.2x margin buffer)
        if budget_eur == BUDGET_CEILING_EUR:
            budget_eur = product.selling_price_eur * quantity * 1.2

    if not intent:
        intent = "Buy all parts required to assemble one Ferrari 296 GTB"

    prepare_new_cascade()
    asyncio.create_task(
        run_cascade(
            intent,
            budget_eur,
            catalogue_product=product,
            quantity=quantity,
            strategy=req.strategy,
            desired_delivery_date=req.desired_delivery_date,
        )
    )
    return {
        "status": "started",
        "intent": intent,
        "product_id": req.product_id,
        "quantity": quantity,
        "desired_delivery_date": req.desired_delivery_date,
    }


class SimulateSupplierFailureRequest(BaseModel):
    agent_id: str


@router.post("/api/simulate/supplier-failure")
async def simulate_supplier_failure_endpoint(req: SimulateSupplierFailureRequest):
    """Simulate 'what if supplier fails?' — returns cost/delay delta and alternate supplier."""
    agent_id = req.agent_id
    result = simulate_supplier_failure(agent_id)
    if result is None:
        return JSONResponse(status_code=400, content={"error": "No completed cascade report; run cascade first"})
    if result.get("error"):
        return JSONResponse(status_code=404, content=result)
    return result


@router.post("/registry/disrupt/{agent_id}")
async def disrupt_agent(agent_id: str):
    agent = registry.get(agent_id)
    if not agent:
        return JSONResponse(status_code=404, content={"error": "Agent not found"})

    msg = LiveMessage(
        message_id=make_id("alert"),
        from_id=agent_id,
        from_label=agent.name,
        to_id="ferrari-procurement-01",
        to_label="Ferrari Procurement",
        type="disruption_alert",
        summary=f"DISRUPTION: {agent.name} reports production halt",
        detail="Manual disruption triggered via API",
        color="#F44336",
        icon="alert",
    )
    registry.log_message(msg)
    return {"status": "disruption_triggered", "agent_id": agent_id}
