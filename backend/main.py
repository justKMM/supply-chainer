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
  Backend serves API only (frontend is separate)
"""

from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.controllers.registry_controller import router as registry_router
from backend.controllers.pubsub_controller import router as pubsub_router
from backend.controllers.reputation_controller import router as reputation_router
from backend.controllers.stream_controller import router as stream_router
from backend.controllers.catalogue_controller import router as catalogue_router
from backend.controllers.policy_controller import router as policy_router
from backend.controllers.escalation_controller import router as escalation_router
from backend.controllers.agent_protocol_controller import router as agent_protocol_router
from backend.controllers.mcp_controller import router as mcp_router
from backend.controllers.a2a_controller import router as a2a_router
from backend.services.agent_service import create_seed_agents
from backend.services.registry_service import registry

app = FastAPI(title="Ferrari Supply Chain Agents", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup: Seed agents into registry ────────────────────────────────────

"""
@app.on_event("startup")
async def startup_seed_agents():
    #Register all seed agents (core, suppliers, MCP, A2A, etc.) on startup.
    agents = create_seed_agents()
    for agent in agents:
        registry.register(agent)
    print(f"✓ Seeded {len(agents)} agents into registry on startup")

"""
# ── Routers ───────────────────────────────────────────────────────────────


app.include_router(registry_router)
app.include_router(catalogue_router)
app.include_router(policy_router)
app.include_router(escalation_router)
app.include_router(pubsub_router)
app.include_router(reputation_router)
app.include_router(stream_router)
app.include_router(agent_protocol_router)
app.include_router(mcp_router)
app.include_router(a2a_router)
