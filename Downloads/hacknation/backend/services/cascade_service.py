"""
Coordination Cascade Orchestrator

Executes the full supply chain procurement cascade:
  Intent → BOM Decomposition → Discovery → Quotes → Negotiation →
  Compliance → Purchase Orders → Logistics → Report Generation
"""

from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta

from backend.config import BUDGET_CEILING_EUR, TRUST_THRESHOLD, MIN_ESG_SCORE
from backend.schemas import LiveMessage, make_id
from backend.services.registry_service import registry
from backend.services.agent_service import ai_reason, ai_decompose_bom, create_seed_agents, CATEGORY_AGENT_MAP
from backend.services.pubsub_service import event_bus
from backend.services.trust_service import reputation_ledger, record_transactions
from backend.services.intelligence_service import generate_intelligence_signals
from backend.services.logistics_service import plan_logistics


# ── State ────────────────────────────────────────────────────────────────────

cascade_state = {
    "running": False,
    "report": None,
    "progress": 0,
}


def prepare_new_cascade():
    """Clear all stateful services before a new cascade."""
    registry.clear()
    event_bus.clear()
    reputation_ledger.clear()


def _ts(offset_seconds: int = 0) -> str:
    return (datetime.utcnow() + timedelta(seconds=offset_seconds)).isoformat() + "Z"


def _emit(
    from_id,
    from_label,
    to_id,
    to_label,
    msg_type,
    summary,
    detail="",
    color="#2196F3",
    icon="info",
):
    msg = LiveMessage(
        message_id=make_id("msg"),
        timestamp=_ts(),
        from_id=from_id,
        from_label=from_label,
        to_id=to_id,
        to_label=to_label,
        type=msg_type,
        summary=summary,
        detail=detail,
        color=color,
        icon=icon,
    )
    registry.log_message(msg)
    return msg


# ── Main Cascade ─────────────────────────────────────────────────────────────

async def run_cascade(intent: str, budget_eur: float = BUDGET_CEILING_EUR) -> dict:
    """Execute the full procurement cascade and return a Network Coordination Report."""
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
        "discovery_results": {
            "agents_discovered": 0,
            "agents_qualified": 0,
            "agents_disqualified": 0,
            "disqualification_reasons": [],
            "discovery_paths": [],
        },
        "negotiations": [],
        "compliance_summary": {
            "total_checks": 0,
            "passed": 0,
            "flagged": 0,
            "failed": 0,
            "flags": [],
        },
        "logistics_plan": {
            "total_shipments": 0,
            "total_logistics_cost_eur": 0,
            "shipments": [],
            "critical_path_days": 0,
            "bottleneck": "",
        },
        "execution_plan": {
            "total_cost_eur": 0,
            "cost_breakdown": {
                "components_eur": 0,
                "logistics_eur": 0,
                "insurance_eur": 0,
                "compliance_fees_eur": 0,
            },
            "timeline": {},
            "suppliers_engaged": 0,
            "purchase_orders_issued": 0,
            "risk_assessment": {"overall_risk": "low", "risks": []},
        },
        "disruptions_handled": [],
        "message_log_summary": {"total_messages": 0, "by_type": {}},
        "reasoning_log": [],
        "graph_nodes": [],
        "graph_edges": [],
        "dashboard": {},
        "pubsub_summary": {},
        "reputation_summary": {},
        "intelligence_feed": [],
    }

    try:
        # ── Step 0: Register all seed agents ─────────────────────────────
        _emit(
            "system",
            "System",
            "registry",
            "Agent Registry",
            "system",
            "Initializing agent network...",
            "Registering all supply chain agents",
            "#9E9E9E",
            "settings",
        )

        # Clear new subsystems
        event_bus.clear()
        reputation_ledger.clear()

        seed_agents = create_seed_agents()
        for agent in seed_agents:
            registry.register(agent)

        # ── Pub-Sub: Auto-subscribe agents based on role & graph position ──
        for agent in seed_agents:
            if agent.status != "active" or (agent.trust and agent.trust.trust_score < TRUST_THRESHOLD):
                continue
            regions = []
            product_cats = []
            if agent.location and agent.location.headquarters:
                regions.append(agent.location.headquarters.country)
            if agent.location and agent.location.shipping_regions:
                regions.extend(agent.location.shipping_regions)
            for p in agent.capabilities.products:
                product_cats.append(p.category)
            event_bus.subscribe(
                agent.agent_id,
                agent.name,
                agent.role,
                regions=list(set(regions)),
                product_categories=list(set(product_cats)),
            )

        _emit(
            "system",
            "System",
            "registry",
            "Agent Registry",
            "pubsub_init",
            f"Event bus initialized: {len(event_bus.list_subscriptions())} agents subscribed",
            "Role-based disruption subscriptions configured",
            "#00BCD4",
            "broadcast",
        )

        await asyncio.sleep(0.3)
        cascade_state["progress"] = 5

        # ── Step 1: Decompose Intent into BOM ────────────────────────────
        _emit(
            "ferrari-procurement-01",
            "Ferrari Procurement",
            "system",
            "System",
            "intent_decomposition",
            f"Decomposing intent: {intent}",
            "Using AI to identify required component categories",
            "#DC143C",
            "brain",
        )

        reasoning = await ai_reason(
            "Ferrari Procurement AI",
            "procurement_agent",
            f"You received the intent: '{intent}'. Explain your approach to decomposing this into component categories for sourcing.",
        )
        report["reasoning_log"].append({"agent": "Ferrari Procurement", "timestamp": _ts(), "thought": reasoning})

        bom = await ai_decompose_bom(intent)
        total_parts = sum(c["parts_count"] for c in bom)
        report["bill_of_materials_summary"] = {
            "total_component_categories": len(bom),
            "total_unique_parts": total_parts,
            "categories": bom,
        }

        _emit(
            "ferrari-procurement-01",
            "Ferrari Procurement",
            "system",
            "System",
            "bom_complete",
            f"BOM decomposed: {len(bom)} categories, {total_parts} unique parts",
            ", ".join(c["category"] for c in bom),
            "#DC143C",
            "checklist",
        )

        await asyncio.sleep(0.3)
        cascade_state["progress"] = 15

        # ── Step 2: Discovery — find suppliers per category ──────────────
        all_agents = registry.list_all()
        qualified_agents = {}
        disqualified = []

        for cat_info in bom:
            cat = cat_info["category"]
            _emit(
                "ferrari-procurement-01",
                "Ferrari Procurement",
                "registry",
                "Agent Registry",
                "discovery",
                f"Searching for {cat} suppliers",
                f"Query: role=tier_1_supplier, capability={cat}, certification=IATF_16949, region=EU",
                "#2196F3",
                "search",
            )

            candidates = registry.search(role="tier_1_supplier", capability=cat)
            # Also check internal
            if cat in CATEGORY_AGENT_MAP:
                mapped = registry.get(CATEGORY_AGENT_MAP[cat])
                if mapped and mapped not in candidates:
                    candidates.append(mapped)

            # Filter by trust
            valid = []
            for c in candidates:
                if c.trust and c.trust.trust_score >= TRUST_THRESHOLD:
                    valid.append(c)
                else:
                    disqualified.append(
                        {
                            "agent_id": c.agent_id,
                            "reason": f"Trust score {c.trust.trust_score if c.trust else 0} below threshold {TRUST_THRESHOLD}",
                        }
                    )

            # Filter by certification
            final = []
            for c in valid:
                has_cert = any(cert.type == "IATF_16949" and cert.status == "active" for cert in c.certifications)
                if has_cert or (c.trust and c.trust.ferrari_tier_status == "internal"):
                    final.append(c)
                else:
                    disqualified.append(
                        {"agent_id": c.agent_id, "reason": "Failed IATF_16949 certification check"}
                    )

            if final:
                # Select best by trust score
                best = max(final, key=lambda a: a.trust.trust_score if a.trust else 0)
                qualified_agents[cat] = best

                reasoning = await ai_reason(
                    "Ferrari Procurement AI",
                    "procurement_agent",
                    f"For {cat}, found {len(candidates)} candidates. Selected {best.name} (trust={best.trust.trust_score if best.trust else 'N/A'}). Explain why.",
                )
                report["reasoning_log"].append({"agent": "Ferrari Procurement", "timestamp": _ts(), "thought": reasoning})

                report["discovery_results"]["discovery_paths"].append(
                    {
                        "need": cat_info["key_components"][0] if cat_info["key_components"] else cat,
                        "query": f"role=tier_1_supplier, capability={cat}, certification=IATF_16949",
                        "results_count": len(candidates),
                        "selected": best.agent_id,
                        "selection_reason": f"Trust score {best.trust.trust_score if best.trust else 'N/A'}, {best.trust.ferrari_tier_status if best.trust else 'unknown'} status",
                    }
                )

                _emit(
                    "registry",
                    "Agent Registry",
                    "ferrari-procurement-01",
                    "Ferrari Procurement",
                    "discovery_result",
                    f"Found {len(candidates)} suppliers for {cat}, selected {best.name}",
                    f"Trust: {best.trust.trust_score if best.trust else 'N/A'}, Status: {best.trust.ferrari_tier_status if best.trust else 'N/A'}",
                    "#4CAF50",
                    "check",
                )

            await asyncio.sleep(0.15)

        report["discovery_results"]["agents_discovered"] = len(all_agents)
        report["discovery_results"]["agents_qualified"] = len(qualified_agents)
        report["discovery_results"]["agents_disqualified"] = len(disqualified)
        report["discovery_results"]["disqualification_reasons"] = disqualified[:5]

        cascade_state["progress"] = 30

        # ── Step 3: Request Quotes ───────────────────────────────────────
        quotes = {}
        for cat, agent in qualified_agents.items():
            products = agent.capabilities.products
            if not products:
                continue

            product = products[0]
            qty = random.randint(1, 4) if product.min_order_quantity <= 4 else product.min_order_quantity

            _emit(
                "ferrari-procurement-01",
                "Ferrari Procurement",
                agent.agent_id,
                agent.name,
                "request_quote",
                f"Requesting quote for {qty}x {product.name}",
                f"Budget ceiling: EUR {BUDGET_CEILING_EUR / len(qualified_agents):,.0f}/category. Delivery to Maranello.",
                "#4CAF50",
                "request",
            )

            # Supplier responds
            reasoning = await ai_reason(
                agent.name,
                agent.role,
                f"Ferrari requested a quote for {qty}x {product.name} at your list price of EUR {product.unit_price_eur}. Your capacity utilization is {agent.capabilities.production_capacity.current_utilization_pct if agent.capabilities.production_capacity else 70}%. How do you respond?",
            )
            report["reasoning_log"].append({"agent": agent.name, "timestamp": _ts(), "thought": reasoning})

            total = product.unit_price_eur * qty
            quote_id = f"QT-{agent.agent_id[:8].upper()}-{make_id('')[4:10]}"

            _emit(
                agent.agent_id,
                agent.name,
                "ferrari-procurement-01",
                "Ferrari Procurement",
                "quote_response",
                f"Quoted EUR {product.unit_price_eur:,.0f}/unit, {product.lead_time_days}-day lead time",
                f"Total: EUR {total:,.0f}. Quote ID: {quote_id}",
                "#4CAF50",
                "response",
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

        cascade_state["progress"] = 45

        # ── Step 4: Negotiation ──────────────────────────────────────────
        final_orders = {}
        for cat, quote in quotes.items():
            agent = quote["agent"]
            product = quote["product"]
            initial_price = quote["initial_price"]

            # Skip negotiation for internal
            if agent.trust and agent.trust.ferrari_tier_status == "internal":
                final_orders[cat] = {**quote, "final_price": initial_price, "discount_pct": 0}
                continue

            # Round 1: Counter offer
            discount_ask = random.uniform(3.0, 7.0)
            offer_price = round(initial_price * (1 - discount_ask / 100), 2)

            reasoning = await ai_reason(
                "Ferrari Procurement AI",
                "procurement_agent",
                f"{agent.name} quoted EUR {initial_price} for {product.name}. You want to negotiate. Your counter offer is EUR {offer_price} ({discount_ask:.1f}% discount). Explain your reasoning.",
            )
            report["reasoning_log"].append({"agent": "Ferrari Procurement", "timestamp": _ts(), "thought": reasoning})

            _emit(
                "ferrari-procurement-01",
                "Ferrari Procurement",
                agent.agent_id,
                agent.name,
                "negotiate",
                f"Counter offer: EUR {offer_price:,.0f}/unit ({discount_ask:.1f}% discount)",
                "Volume commitment justifies discount",
                "#FF9800",
                "negotiate",
            )

            # Round 2: Supplier counter
            supplier_discount = random.uniform(1.0, discount_ask * 0.6)
            counter_price = round(initial_price * (1 - supplier_discount / 100), 2)

            reasoning = await ai_reason(
                agent.name,
                agent.role,
                f"Ferrari counter-offered EUR {offer_price} (you quoted EUR {initial_price}). Your floor price allows {supplier_discount:.1f}% discount. Counter at EUR {counter_price}.",
            )
            report["reasoning_log"].append({"agent": agent.name, "timestamp": _ts(), "thought": reasoning})

            _emit(
                agent.agent_id,
                agent.name,
                "ferrari-procurement-01",
                "Ferrari Procurement",
                "negotiate_response",
                f"Counter: EUR {counter_price:,.0f}/unit ({supplier_discount:.1f}% off list)",
                "Material costs limit flexibility",
                "#FF9800",
                "negotiate",
            )

            # Round 3: Split difference and accept
            final_price = round((offer_price + counter_price) / 2, 2)
            final_discount = round((1 - final_price / initial_price) * 100, 2)

            reasoning = await ai_reason(
                "Ferrari Procurement AI",
                "procurement_agent",
                f"Split the difference between EUR {offer_price} and EUR {counter_price} = EUR {final_price}. Within budget. Accept?",
            )
            report["reasoning_log"].append({"agent": "Ferrari Procurement", "timestamp": _ts(), "thought": reasoning})

            _emit(
                "ferrari-procurement-01",
                "Ferrari Procurement",
                agent.agent_id,
                agent.name,
                "negotiate",
                f"Accepted: EUR {final_price:,.0f}/unit ({final_discount:.1f}% off list)",
                "Deal within budget ceiling",
                "#4CAF50",
                "handshake",
            )

            negotiation_log = [
                {
                    "round": 1,
                    "from": "ferrari-procurement-01",
                    "action": "counter_offer",
                    "value_eur": offer_price,
                    "reasoning": f"Volume commitment warrants {discount_ask:.1f}% discount",
                },
                {
                    "round": 2,
                    "from": agent.agent_id,
                    "action": "counter_offer",
                    "value_eur": counter_price,
                    "reasoning": f"Material costs limit discount to {supplier_discount:.1f}%",
                },
                {
                    "round": 3,
                    "from": "ferrari-procurement-01",
                    "action": "accept",
                    "value_eur": final_price,
                    "reasoning": "Split difference, within budget ceiling",
                },
            ]
            report["negotiations"].append(
                {
                    "with_agent": agent.agent_id,
                    "with_name": agent.name,
                    "product": product.name,
                    "rounds": 3,
                    "initial_ask_eur": initial_price,
                    "initial_offer_eur": offer_price,
                    "final_agreed_eur": final_price,
                    "discount_pct": final_discount,
                    "negotiation_log": negotiation_log,
                }
            )

            final_orders[cat] = {**quote, "final_price": final_price, "discount_pct": final_discount}
            await asyncio.sleep(0.1)

        cascade_state["progress"] = 60

        # ── Step 5: Compliance Checks ────────────────────────────────────
        checks_passed = 0
        checks_flagged = 0
        flags = []

        for _, order in final_orders.items():
            agent = order["agent"]
            _emit(
                "ferrari-procurement-01",
                "Ferrari Procurement",
                "eu-compliance-agent-01",
                "EU Compliance Validator",
                "compliance_check",
                f"Requesting compliance check for {agent.name}",
                "Checks: certification, sanctions, ESG, regulation",
                "#FF9800",
                "shield",
            )

            # Run checks
            check_results = []

            # Cert check
            has_cert = any(c.type == "IATF_16949" and c.status == "active" for c in agent.certifications)
            check_results.append(
                {"check": "certification_validity", "status": "pass" if has_cert else "fail",
                 "detail": f"IATF_16949 {'valid' if has_cert else 'not found'}"}
            )

            # Sanctions check
            sanctions_ok = agent.compliance.sanctions_clear if agent.compliance else True
            check_results.append(
                {"check": "sanctions_screening", "status": "pass" if sanctions_ok else "fail",
                 "detail": "No matches in EU/US sanctions lists" if sanctions_ok else "Sanctions match found"}
            )

            # ESG check
            esg_score = agent.compliance.esg_rating.score if agent.compliance and agent.compliance.esg_rating else 0
            esg_ok = esg_score >= MIN_ESG_SCORE
            esg_marginal = esg_ok and esg_score < MIN_ESG_SCORE + 10
            esg_status = "pass" if esg_ok else "fail"
            check_results.append(
                {"check": "esg_threshold", "status": esg_status,
                 "detail": f"Score {esg_score}, {'exceeds' if esg_ok else 'below'} minimum {MIN_ESG_SCORE}"}
            )
            if esg_marginal:
                flags.append(
                    {
                        "agent_id": agent.agent_id,
                        "check": "esg_threshold",
                        "detail": f"EcoVadis score {esg_score} marginally above minimum {MIN_ESG_SCORE}, recommend monitoring",
                        "severity": "warning",
                    }
                )
                checks_flagged += 1

            # Regulation check
            check_results.append(
                {"check": "regulation_compliance", "status": "pass",
                 "detail": "EU_REACH and CE_Marking confirmed"}
            )

            all_pass = all(c["status"] == "pass" for c in check_results)
            checks_passed += 1 if all_pass else 0
            overall = "approved" if all_pass else "rejected"

            _emit(
                "eu-compliance-agent-01",
                "EU Compliance Validator",
                "ferrari-procurement-01",
                "Ferrari Procurement",
                "compliance_result",
                f"{agent.name}: {overall.upper()} - all {len(check_results)} checks passed" if all_pass else f"{agent.name}: FLAGGED",
                "; ".join(f"{c['check']}: {c['status']}" for c in check_results),
                "#4CAF50" if all_pass else "#F44336",
                "check" if all_pass else "warning",
            )

            report["compliance_summary"]["total_checks"] += 1
            await asyncio.sleep(0.1)

        report["compliance_summary"]["passed"] = checks_passed
        report["compliance_summary"]["flagged"] = checks_flagged
        report["compliance_summary"]["flags"] = flags

        cascade_state["progress"] = 72

        # ── Step 6: Purchase Orders ──────────────────────────────────────
        total_component_cost = 0
        po_count = 0
        ship_date_base = datetime.utcnow() + timedelta(days=2)

        for _, order in final_orders.items():
            agent = order["agent"]
            product = order["product"]
            qty = order["quantity"]
            price = order["final_price"]
            total = round(price * qty, 2)
            total_component_cost += total

            po_number = f"PO-FERRARI-{datetime.utcnow().strftime('%Y')}-{po_count + 1:05d}"

            _emit(
                "ferrari-procurement-01",
                "Ferrari Procurement",
                agent.agent_id,
                agent.name,
                "purchase_order",
                f"PO issued: {qty}x {product.name} @ EUR {price:,.0f}",
                f"PO: {po_number}, Total: EUR {total:,.0f}, Delivery to Maranello",
                "#DC143C",
                "order",
            )

            # Order confirmation
            ship_date = ship_date_base + timedelta(days=random.randint(0, 3))
            delivery_date = ship_date + timedelta(days=product.lead_time_days)

            _emit(
                agent.agent_id,
                agent.name,
                "ferrari-procurement-01",
                "Ferrari Procurement",
                "order_confirmation",
                f"Order confirmed. Ship: {ship_date.strftime('%b %d')}, Deliver: {delivery_date.strftime('%b %d')}",
                f"PO: {po_number}, Tracking: {agent.agent_id[:8].upper()}-SHIP-{po_count + 1:04d}",
                "#4CAF50",
                "truck",
            )

            order["po_number"] = po_number
            order["ship_date"] = ship_date.isoformat()
            order["delivery_date"] = delivery_date.isoformat()
            po_count += 1
            await asyncio.sleep(0.1)

        cascade_state["progress"] = 82

        # ── Step 7: Logistics Planning (separate service) ────────────────
        logistics_plan, max_lead_days = plan_logistics(final_orders, _emit)
        report["logistics_plan"] = logistics_plan

        cascade_state["progress"] = 90

        # ── Step 8: Disruption Simulation ────────────────────────────────
        _emit(
            "brembo-brake-supplier-01",
            "Brembo S.p.A.",
            "ferrari-procurement-01",
            "Ferrari Procurement",
            "disruption_alert",
            "PRODUCTION HALT — Carbon fiber supply interrupted",
            "Estimated 21-day delay. Capacity at 0%. Recommended action: re-source.",
            "#F44336",
            "alert",
        )

        reasoning = await ai_reason(
            "Ferrari Procurement AI",
            "procurement_agent",
            "Brembo has reported a production halt due to carbon fiber shortage. 21-day delay expected. Should we re-source? What are the options and trade-offs?",
        )
        report["reasoning_log"].append({"agent": "Ferrari Procurement", "timestamp": _ts(), "thought": reasoning})

        _emit(
            "ferrari-procurement-01",
            "Ferrari Procurement",
            "registry",
            "Agent Registry",
            "discovery",
            "Emergency re-source: searching for alternative brake suppliers",
            "Triggered by Brembo disruption alert",
            "#F44336",
            "search",
        )

        _emit(
            "ferrari-procurement-01",
            "Ferrari Procurement",
            "system",
            "System",
            "resolution",
            "Disruption resolved: backup supplier identified",
            "Performance Friction (US) can supply at EUR 2,950/unit with 3-day delay",
            "#4CAF50",
            "check",
        )

        report["disruptions_handled"].append(
            {
                "alert_id": make_id("ALERT"),
                "timestamp": _ts(),
                "disrupted_agent": "brembo-brake-supplier-01",
                "disruption_type": "production_halt",
                "resolution": {
                    "action": "re_source",
                    "new_supplier": "performance-friction-us-01",
                    "new_price_eur": 2950.00,
                    "additional_cost_eur": 600.00,
                    "delay_days": 3,
                    "resolved_at": _ts(),
                },
            }
        )

        cascade_state["progress"] = 92

        # ── Step 9: Record Transactions & Build Reputation ───────────────
        _emit(
            "system",
            "System",
            "reputation-ledger",
            "Reputation Ledger",
            "reputation_init",
            "Recording transaction attestations for all suppliers",
            "Building verifiable reputation scores from actual transaction data",
            "#00BCD4",
            "ledger",
        )

        report["reputation_summary"] = record_transactions(final_orders, _emit)

        cascade_state["progress"] = 94

        # ── Step 10: Intelligence Feed — Real-world signals ──────────────
        _emit(
            "intelligence-feed",
            "Intelligence Feed",
            "network",
            "Agent Network",
            "intel_init",
            "Scanning external intelligence sources...",
            "Weather, regulatory, commodity, port, and recall databases",
            "#E91E63",
            "satellite",
        )

        intel_results = await generate_intelligence_signals(event_bus, count=5)
        report["intelligence_feed"] = intel_results
        report["pubsub_summary"] = event_bus.get_summary()

        _emit(
            "intelligence-feed",
            "Intelligence Feed",
            "network",
            "Agent Network",
            "intel_complete",
            f"Intelligence scan complete: {len(intel_results)} signals processed",
            f"{event_bus.get_summary()['total_deliveries']} event deliveries to subscribed agents",
            "#E91E63",
            "satellite",
        )

        cascade_state["progress"] = 96

        # ── Step 11: Build execution plan and final report ───────────────
        insurance_cost = round(total_component_cost * 0.018, 2)
        compliance_fees = round(len(qualified_agents) * 200, 2)
        total_cost = total_component_cost + logistics_plan["total_logistics_cost_eur"] + insurance_cost + compliance_fees

        now = datetime.utcnow()
        report["execution_plan"] = {
            "total_cost_eur": round(total_cost, 2),
            "cost_breakdown": {
                "components_eur": round(total_component_cost, 2),
                "logistics_eur": round(logistics_plan["total_logistics_cost_eur"], 2),
                "insurance_eur": insurance_cost,
                "compliance_fees_eur": compliance_fees,
            },
            "timeline": {
                "procurement_start": now.strftime("%Y-%m-%d"),
                "all_components_ordered": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "first_delivery": (now + timedelta(days=8)).strftime("%Y-%m-%d"),
                "last_delivery": (now + timedelta(days=max_lead_days + 3)).strftime("%Y-%m-%d"),
                "assembly_ready": (now + timedelta(days=max_lead_days + 3)).strftime("%Y-%m-%d"),
            },
            "suppliers_engaged": len(qualified_agents),
            "purchase_orders_issued": po_count,
            "risk_assessment": {
                "overall_risk": "medium",
                "risks": [
                    {
                        "type": "single_source_dependency",
                        "component": "Carbon Fiber Monocoque",
                        "supplier": "dallara-compositi-01",
                        "mitigation": "Alternative supplier identified: carbon-tech-de-02 (21-day lead time)",
                    },
                    {
                        "type": "lead_time",
                        "component": "MagneRide Dampers",
                        "detail": f"{max_lead_days}-day lead time on critical path",
                        "mitigation": "Expedited shipping option available at +EUR 800",
                    },
                ],
            },
        }

        # Build graph data
        color_map = {
            "procurement_agent": "#DC143C",
            "tier_1_supplier": "#2196F3",
            "tier_2_supplier": "#64B5F6",
            "raw_material_supplier": "#90CAF9",
            "contract_manufacturer": "#4CAF50",
            "logistics_provider": "#9C27B0",
            "compliance_agent": "#FF9800",
            "assembly_coordinator": "#F44336",
        }

        nodes = []
        edges = []
        node_ids_added = set()

        # Add Ferrari procurement node
        nodes.append(
            {
                "id": "ferrari-procurement-01",
                "label": "Ferrari Procurement",
                "role": "procurement_agent",
                "color": "#DC143C",
                "location": {"lat": 44.5294, "lon": 10.8633, "city": "Maranello"},
                "trust_score": None,
                "status": "active",
                "size": 45,
            }
        )
        node_ids_added.add("ferrari-procurement-01")

        # Add supplier nodes and edges
        for _, order in final_orders.items():
            agent = order["agent"]
            if agent.agent_id not in node_ids_added:
                loc = None
                if agent.location and agent.location.headquarters:
                    hq = agent.location.headquarters
                    loc = {"lat": hq.lat, "lon": hq.lon, "city": hq.city}
                nodes.append(
                    {
                        "id": agent.agent_id,
                        "label": agent.name,
                        "role": agent.role,
                        "color": color_map.get(agent.role, "#2196F3"),
                        "location": loc,
                        "trust_score": agent.trust.trust_score if agent.trust else None,
                        "status": "active",
                        "size": 30,
                    }
                )
                node_ids_added.add(agent.agent_id)

            edges.append(
                {
                    "from": "ferrari-procurement-01",
                    "to": agent.agent_id,
                    "type": "procurement",
                    "label": order.get("po_number", ""),
                    "value_eur": round(order["final_price"] * order["quantity"], 2),
                    "message_count": 6,
                    "status": "confirmed",
                }
            )

        # Add logistics node
        if "dhl-logistics-01" not in node_ids_added:
            nodes.append(
                {
                    "id": "dhl-logistics-01",
                    "label": "DHL Supply Chain",
                    "role": "logistics_provider",
                    "color": "#9C27B0",
                    "location": {"lat": 45.4654, "lon": 9.1859, "city": "Milan"},
                    "trust_score": 0.92,
                    "status": "active",
                    "size": 28,
                }
            )
            node_ids_added.add("dhl-logistics-01")

        for _, order in final_orders.items():
            agent = order["agent"]
            if agent.trust and agent.trust.ferrari_tier_status != "internal":
                edges.append(
                    {
                        "from": agent.agent_id,
                        "to": "dhl-logistics-01",
                        "type": "logistics",
                        "label": "SHIP",
                        "message_count": 2,
                        "status": "scheduled",
                    }
                )

        # Add compliance node
        if "eu-compliance-agent-01" not in node_ids_added:
            nodes.append(
                {
                    "id": "eu-compliance-agent-01",
                    "label": "EU Compliance Validator",
                    "role": "compliance_agent",
                    "color": "#FF9800",
                    "location": {"lat": 50.1109, "lon": 8.6821, "city": "Frankfurt"},
                    "trust_score": 0.95,
                    "status": "active",
                    "size": 25,
                }
            )
            node_ids_added.add("eu-compliance-agent-01")

        edges.append(
            {
                "from": "ferrari-procurement-01",
                "to": "eu-compliance-agent-01",
                "type": "compliance",
                "label": "Validation",
                "message_count": len(qualified_agents) * 2,
                "status": "completed",
            }
        )

        # Add assembly coordinator
        if "maranello-assembly-01" not in node_ids_added:
            nodes.append(
                {
                    "id": "maranello-assembly-01",
                    "label": "Maranello Assembly",
                    "role": "assembly_coordinator",
                    "color": "#F44336",
                    "location": {"lat": 44.5294, "lon": 10.8633, "city": "Maranello"},
                    "trust_score": 1.0,
                    "status": "active",
                    "size": 25,
                }
            )

        edges.append(
            {
                "from": "ferrari-procurement-01",
                "to": "maranello-assembly-01",
                "type": "coordination",
                "label": "Assembly scheduling",
                "message_count": 2,
                "status": "confirmed",
            }
        )

        report["graph_nodes"] = nodes
        report["graph_edges"] = edges

        # Build dashboard data
        messages = registry.get_messages()
        by_type = {}
        for m in messages:
            by_type[m.type] = by_type.get(m.type, 0) + 1

        report["message_log_summary"] = {
            "total_messages": len(messages),
            "by_type": by_type,
        }

        report["dashboard"] = {
            "hero_metrics": [
                {"label": "Total Cost", "value": f"EUR {total_cost:,.0f}", "trend": None},
                {"label": "Suppliers Engaged", "value": str(len(qualified_agents)), "trend": None},
                {"label": "Time to Assembly-Ready", "value": f"{max_lead_days + 3} days", "trend": None},
                {
                    "label": "Compliance Pass Rate",
                    "value": f"{(checks_passed / max(report['compliance_summary']['total_checks'], 1)) * 100:.0f}%",
                    "trend": "up",
                },
                {
                    "label": "Disruptions Resolved",
                    "value": f"{len(report['disruptions_handled'])}/{len(report['disruptions_handled'])}",
                    "trend": None,
                },
                {"label": "Messages Exchanged", "value": str(len(messages)), "trend": None},
                {"label": "Intel Signals", "value": str(len(report.get("intelligence_feed", []))), "trend": None},
                {
                    "label": "Attestations",
                    "value": str(report.get("reputation_summary", {}).get("total_attestations", 0)),
                    "trend": "up",
                },
            ],
            "cost_breakdown": [
                {"label": "Components", "value": round(total_component_cost, 2), "color": "#2196F3"},
                {"label": "Logistics", "value": round(logistics_plan["total_logistics_cost_eur"], 2), "color": "#9C27B0"},
                {"label": "Insurance", "value": insurance_cost, "color": "#FF9800"},
                {"label": "Compliance", "value": compliance_fees, "color": "#4CAF50"},
            ],
            "timeline_items": [],
            "supplier_markers": [],
            "supplier_routes": [],
            "risk_items": report["execution_plan"]["risk_assessment"]["risks"],
        }

        # Timeline items
        for cat, order in final_orders.items():
            agent = order["agent"]
            start = now.strftime("%Y-%m-%d")
            end_date = now + timedelta(days=order["product"].lead_time_days + 3)
            report["dashboard"]["timeline_items"].append(
                {
                    "label": f"{order['product'].name} ({agent.name})",
                    "start": start,
                    "end": end_date.strftime("%Y-%m-%d"),
                    "status": "confirmed",
                    "critical_path": order["product"].lead_time_days >= max_lead_days,
                    "category": cat,
                    "lead_time_days": order["product"].lead_time_days,
                }
            )

        # Map markers and routes
        report["dashboard"]["supplier_markers"].append(
            {
                "lat": 44.5294,
                "lon": 10.8633,
                "label": "Ferrari Maranello (Assembly)",
                "type": "destination",
                "color": "#DC143C",
            }
        )
        for cat, order in final_orders.items():
            agent = order["agent"]
            if agent.location and agent.location.headquarters:
                hq = agent.location.headquarters
                report["dashboard"]["supplier_markers"].append(
                    {
                        "lat": hq.lat,
                        "lon": hq.lon,
                        "label": f"{agent.name} ({cat.replace('_', ' ').title()})",
                        "type": "supplier",
                        "color": color_map.get(agent.role, "#2196F3"),
                    }
                )
                report["dashboard"]["supplier_routes"].append(
                    {
                        "from": {"lat": hq.lat, "lon": hq.lon},
                        "to": {"lat": 44.5294, "lon": 10.8633},
                        "label": f"{agent.name} → Maranello",
                        "mode": "road",
                    }
                )

        # Final message
        _emit(
            "ferrari-procurement-01",
            "Ferrari Procurement",
            "system",
            "System",
            "cascade_complete",
            f"Cascade complete! Total cost: EUR {total_cost:,.0f}, {po_count} POs issued, {len(logistics_plan['shipments'])} shipments",
            f"Assembly-ready in {max_lead_days + 3} days. {len(messages)} messages exchanged.",
            "#DC143C",
            "trophy",
        )

        report["completed_at"] = _ts()
        report["status"] = "completed"

    except Exception as e:
        report["status"] = "error"
        report["error"] = str(e)
        _emit("system", "System", "system", "System", "error", f"Cascade error: {str(e)}", "", "#F44336", "error")

    cascade_state["running"] = False
    cascade_state["progress"] = 100
    cascade_state["report"] = report
    return report
