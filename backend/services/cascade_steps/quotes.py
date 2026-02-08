"""Cascade step: request quotes and collect responses."""

from __future__ import annotations

import asyncio
import random

from backend.services.agent_service import ai_reason
from backend.config import BUDGET_CEILING_EUR
from backend.schemas import make_id


async def run_quotes(qualified_agents: dict, report: dict, emit, ts) -> dict:
    quotes = {}
    for cat, agent in qualified_agents.items():
        products = agent.capabilities.products
        if not products:
            continue

        product = products[0]
        qty = random.randint(1, 4) if product.min_order_quantity <= 4 else product.min_order_quantity

        emit(
            "ferrari-procurement-01",
            "Ferrari Procurement",
            agent.agent_id,
            agent.name,
            "request_quote",
            summary=None,
            payload={
                "product_name": product.name,
                "quantity": qty,
                "budget_ceiling_eur": BUDGET_CEILING_EUR / max(len(qualified_agents), 1),
            },
        )

        reasoning = await ai_reason(
            agent.name,
            agent.role,
            f"Ferrari requested a quote for {qty}x {product.name} at your list price of EUR {product.unit_price_eur}. Your capacity utilization is {agent.capabilities.production_capacity.current_utilization_pct if agent.capabilities.production_capacity else 70}%. How do you respond?",
        )
        report["reasoning_log"].append({"agent": agent.name, "timestamp": ts(), "thought": reasoning})

        total = product.unit_price_eur * qty
        quote_id = f"QT-{agent.agent_id[:8].upper()}-{make_id('')[4:10]}"

        emit(
            agent.agent_id,
            agent.name,
            "ferrari-procurement-01",
            "Ferrari Procurement",
            "quote_response",
            summary=None,
            payload={
                "unit_price_eur": product.unit_price_eur,
                "lead_time_days": product.lead_time_days,
                "total_eur": total,
                "quote_id": quote_id,
            },
        )

        quotes[cat] = {
            "agent": agent,
            "product": product,
            "quantity": qty,
            "quote_id": quote_id,
            "initial_price": product.unit_price_eur,
            "total": total,
        }
        await asyncio.sleep(0.1)

    return quotes
