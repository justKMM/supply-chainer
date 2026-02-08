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
app.include_router(registry_router)
app.include_router(catalogue_router)
app.include_router(policy_router)
app.include_router(escalation_router)
app.include_router(pubsub_router)
app.include_router(reputation_router)
app.include_router(stream_router)
app.include_router(agent_protocol_router)
