from __future__ import annotations

import asyncio

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.schemas import AgentFact, TriggerRequest, LiveMessage, make_id
from backend.services.cascade_service import run_cascade, cascade_state, prepare_new_cascade
from backend.services.registry_service import registry

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
    min_trust: float = Query(0.0),
):
    results = registry.search(
        role=role,
        capability=capability,
        region=region,
        certification=certification,
        min_trust=min_trust,
    )
    return results


@router.get("/registry/list")
async def list_agents():
    return registry.list_all()


@router.get("/registry/agent/{agent_id}")
async def get_agent(agent_id: str):
    agent = registry.get(agent_id)
    if not agent:
        return JSONResponse(status_code=404, content={"error": "Agent not found"})
    return agent


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

    prepare_new_cascade()

    # Run cascade in background
    asyncio.create_task(run_cascade(req.intent, req.budget_eur))
    return {"status": "started", "intent": req.intent}


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
