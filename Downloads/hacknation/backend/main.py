"""
FastAPI application — the backbone of the Ferrari Supply Chain Agent Network.

Endpoints:
  POST   /registry/register           → Register an agent
  GET    /registry/search             → Discover agents
  GET    /registry/list               → List all agents
  GET    /registry/agent/{agent_id}   → Get single agent
  DELETE /registry/deregister/{id}    → Remove agent
  POST   /registry/log                → Log a message
  GET    /registry/logs               → Get all messages
  POST   /registry/trigger            → Kick off cascade
  POST   /registry/disrupt/{agent_id} → Simulate disruption
  GET    /api/stream                  → SSE live message feed
  GET    /api/report                  → Get latest report
  GET    /api/progress                → Get cascade progress
  GET    /                            → Serve frontend
"""

from __future__ import annotations
import asyncio, json, os
from pathlib import Path
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import AgentFact, TriggerRequest, LiveMessage, make_id
from backend.registry import registry
from backend.cascade import run_cascade, cascade_state
from backend.pubsub import event_bus
from backend.reputation import reputation_ledger

app = FastAPI(title="Ferrari Supply Chain Agents", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Registry Endpoints ───────────────────────────────────────────────────────

@app.post("/registry/register", status_code=201)
async def register_agent(agent: AgentFact):
    return registry.register(agent)


@app.get("/registry/search")
async def search_agents(
    role: str | None = Query(None),
    capability: str | None = Query(None),
    region: str | None = Query(None),
    certification: str | None = Query(None),
    min_trust: float = Query(0.0),
):
    results = registry.search(role=role, capability=capability, region=region,
                              certification=certification, min_trust=min_trust)
    return results


@app.get("/registry/list")
async def list_agents():
    return registry.list_all()


@app.get("/registry/agent/{agent_id}")
async def get_agent(agent_id: str):
    agent = registry.get(agent_id)
    if not agent:
        return JSONResponse(status_code=404, content={"error": "Agent not found"})
    return agent


@app.delete("/registry/deregister/{agent_id}", status_code=204)
async def deregister_agent(agent_id: str):
    registry.deregister(agent_id)


@app.post("/registry/log", status_code=201)
async def log_message(msg: LiveMessage):
    registry.log_message(msg)
    return {"status": "logged"}


@app.get("/registry/logs")
async def get_logs():
    return registry.get_messages()


# ── Cascade Trigger ──────────────────────────────────────────────────────────

@app.post("/registry/trigger")
async def trigger_cascade(req: TriggerRequest):
    if cascade_state["running"]:
        return JSONResponse(status_code=409, content={"error": "Cascade already running"})

    # Clear previous state
    registry.clear()
    event_bus.clear()
    reputation_ledger.clear()

    # Run cascade in background
    asyncio.create_task(run_cascade(req.intent, req.budget_eur))
    return {"status": "started", "intent": req.intent}


@app.post("/registry/disrupt/{agent_id}")
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


# ── Pub-Sub Endpoints ────────────────────────────────────────────────────────

@app.get("/api/pubsub/summary")
async def pubsub_summary():
    return event_bus.get_summary()


@app.get("/api/pubsub/events")
async def pubsub_events():
    return [e.model_dump() for e in event_bus.get_events()]


@app.get("/api/pubsub/subscriptions")
async def pubsub_subscriptions():
    return [s.model_dump() for s in event_bus.list_subscriptions()]


# ── Reputation Endpoints ────────────────────────────────────────────────────

@app.get("/api/reputation/summary")
async def reputation_summary():
    return reputation_ledger.get_summary()


@app.get("/api/reputation/scores")
async def reputation_scores():
    return [s.model_dump() for s in reputation_ledger.get_all_scores()]


@app.get("/api/reputation/agent/{agent_id}")
async def reputation_agent(agent_id: str):
    score = reputation_ledger.get_score(agent_id)
    if not score:
        return JSONResponse(status_code=404, content={"error": "No reputation data"})
    chain = reputation_ledger.verify_chain(agent_id)
    attestations = reputation_ledger.get_attestations(agent_id)
    return {
        "score": score.model_dump(),
        "chain_verification": chain,
        "attestations": [a.model_dump() for a in attestations[-10:]],
    }


# ── SSE Stream ───────────────────────────────────────────────────────────────

@app.get("/api/stream")
async def stream_messages():
    queue = registry.subscribe()

    async def event_generator():
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=30)
                    data = msg.model_dump()
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            registry.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/report")
async def get_report():
    if cascade_state["report"]:
        return cascade_state["report"]
    return JSONResponse(status_code=404, content={"error": "No report available yet"})


@app.get("/api/progress")
async def get_progress():
    return {
        "running": cascade_state["running"],
        "progress": cascade_state["progress"],
    }


# ── Serve Frontend ───────────────────────────────────────────────────────────

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
