from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.services.trust_service import reputation_ledger

router = APIRouter()


# ── Reputation Endpoints ────────────────────────────────────────────────────

@router.get("/api/reputation/summary")
async def reputation_summary():
    return reputation_ledger.get_summary()


@router.get("/api/reputation/scores")
async def reputation_scores():
    return [s.model_dump() for s in reputation_ledger.get_all_scores()]


@router.get("/api/reputation/agent/{agent_id}")
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
