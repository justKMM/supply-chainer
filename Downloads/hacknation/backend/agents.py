"""
AI-powered supply chain agents with OpenAI reasoning.

Each agent is an independent actor that can:
- Reason about decisions using OpenAI
- Communicate via the message schema
- Be discovered through the registry
"""

from __future__ import annotations
import json, asyncio
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY, OPENAI_MODEL
from backend.schemas import (
    AgentFact, Capabilities, Product, ProductionCapacity,
    Identity, Certification, LocationInfo, Location, SiteInfo,
    Compliance, ESGRating, Policies, InsuranceInfo, Trust,
    NetworkInfo, UpstreamDependency, LiveMessage, make_id,
)

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ── OpenAI reasoning helper ─────────────────────────────────────────────────

async def ai_reason(agent_name: str, role: str, prompt: str) -> str:
    """Ask OpenAI to reason as a specific supply-chain agent."""
    try:
        resp = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are {agent_name}, a {role} in Ferrari's supply chain network. "
                        "You make realistic business decisions. Be concise (2-3 sentences). "
                        "Respond with business reasoning only, no markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Reasoning unavailable: {e}]"


async def ai_decompose_bom(intent: str) -> list[dict]:
    """Use OpenAI to decompose an intent into a Bill of Materials."""
    try:
        resp = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Ferrari production engineer. Given a procurement intent, "
                        "decompose it into component categories needed. Return ONLY valid JSON array. "
                        "Each item: {\"category\": str, \"parts_count\": int, "
                        "\"key_components\": [str, str, str]}. "
                        "Include: powertrain, braking_system, body_chassis, electronics, "
                        "interior, suspension, wheels_tires, exhaust_emissions."
                    ),
                },
                {"role": "user", "content": intent},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        text = resp.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return _default_bom()


def _default_bom() -> list[dict]:
    return [
        {"category": "powertrain", "parts_count": 12,
         "key_components": ["V6 Engine Block", "Turbocharger Assembly", "8-Speed DCT Gearbox"]},
        {"category": "braking_system", "parts_count": 6,
         "key_components": ["Carbon Ceramic Disc 396mm", "Brake Caliper Set", "Brake Fluid Reservoir"]},
        {"category": "body_chassis", "parts_count": 8,
         "key_components": ["Carbon Fiber Monocoque", "Aluminum Subframe", "Body Panels"]},
        {"category": "electronics", "parts_count": 9,
         "key_components": ["ECU", "Infotainment Unit", "Sensor Array"]},
        {"category": "interior", "parts_count": 5,
         "key_components": ["Leather Seat Assembly", "Steering Wheel", "Dashboard Module"]},
        {"category": "suspension", "parts_count": 4,
         "key_components": ["MagneRide Dampers", "Control Arms", "Anti-Roll Bar"]},
        {"category": "wheels_tires", "parts_count": 2,
         "key_components": ["Forged Alloy Wheels 20\"", "Pirelli P Zero Tires"]},
        {"category": "exhaust_emissions", "parts_count": 1,
         "key_components": ["Catalytic Converter + Exhaust System"]},
    ]


# ── Seed Data: Pre-built AgentFacts for all supply chain actors ─────────────

def create_seed_agents() -> list[AgentFact]:
    """Create realistic supplier agents for the Ferrari supply chain."""
    agents = []

    # 1. Ferrari Procurement Agent
    agents.append(AgentFact(
        agent_id="ferrari-procurement-01",
        name="Ferrari Procurement AI",
        role="procurement_agent",
        description="Central procurement intelligence for Ferrari S.p.A. Decomposes purchase intents, discovers suppliers, negotiates contracts, and orchestrates the full supply cascade.",
        capabilities=Capabilities(
            services=["intent_decomposition", "supplier_discovery", "negotiation", "order_management"],
        ),
        identity=Identity(legal_entity="Ferrari S.p.A.", registration_country="IT", vat_id="IT00159560366"),
        location=LocationInfo(
            headquarters=Location(lat=44.5294, lon=10.8633, city="Maranello", country="IT"),
        ),
        trust=Trust(trust_score=1.0, years_in_operation=78, ferrari_tier_status="internal", past_contracts=0),
        network=NetworkInfo(
            endpoint="http://localhost:8000/agent/ferrari-procurement-01",
            supported_message_types=["request_quote", "negotiate", "purchase_order", "disruption_alert"],
        ),
    ))

    # 2. Brembo — Brakes
    agents.append(AgentFact(
        agent_id="brembo-brake-supplier-01",
        name="Brembo S.p.A.",
        role="tier_1_supplier",
        description="World-leading manufacturer of high-performance braking systems for automotive and motorsport applications.",
        capabilities=Capabilities(
            products=[
                Product(product_id="carbon-ceramic-disc-396mm", name="Carbon Ceramic Brake Disc 396mm",
                        category="braking_system", subcategory="disc",
                        specifications={"material": "carbon_ceramic", "diameter_mm": 396, "weight_kg": 4.2},
                        unit_price_eur=2800.00, min_order_quantity=50, lead_time_days=14),
                Product(product_id="brake-caliper-6pot", name="6-Piston Brake Caliper Set",
                        category="braking_system", subcategory="caliper",
                        specifications={"material": "aluminum_alloy", "pistons": 6},
                        unit_price_eur=1200.00, min_order_quantity=20, lead_time_days=10),
            ],
            services=["custom_engineering", "oem_supply", "testing_validation"],
            production_capacity=ProductionCapacity(units_per_month=15000, current_utilization_pct=72),
        ),
        identity=Identity(legal_entity="Brembo S.p.A.", registration_country="IT", vat_id="IT00222620163"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="TUV SUD", valid_until="2026-08-15"),
            Certification(type="ISO_14001", description="Environmental Management", issued_by="DNV GL", valid_until="2026-03-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=45.6833, lon=9.6150, city="Curno", country="IT"),
            manufacturing_sites=[SiteInfo(site_id="brembo-curno", city="Curno", country="IT", lat=45.6833, lon=9.6150, capabilities=["casting", "machining", "assembly"])],
            shipping_regions=["EU", "NA", "APAC"],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "EU_ELV_Directive", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="EcoVadis", score=72, tier="Gold", valid_until="2026-01-01")),
        policies=Policies(payment_terms="Net 60", incoterms=["EXW", "DAP", "CIF"], accepted_currencies=["EUR", "USD"],
                          insurance=InsuranceInfo(product_liability=True, max_coverage_eur=50000000), min_contract_value_eur=10000, nda_required=True),
        trust=Trust(trust_score=0.94, years_in_operation=63, ferrari_tier_status="approved_supplier", past_contracts=847, on_time_delivery_pct=96.2, defect_rate_ppm=12, dispute_count_12m=0),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/brembo-brake-supplier-01",
                            supported_message_types=["request_quote", "negotiate", "purchase_order", "shipment_update"]),
        upstream_dependencies=[
            UpstreamDependency(material="Carbon fiber prepreg", typical_supplier_role="tier_2_supplier", critical=True),
            UpstreamDependency(material="Aluminum alloy billets", typical_supplier_role="raw_material_supplier", critical=False),
        ],
    ))

    # 3. Dallara Compositi — Body/Chassis
    agents.append(AgentFact(
        agent_id="dallara-compositi-01",
        name="Dallara Compositi S.r.l.",
        role="tier_1_supplier",
        description="Specialist in carbon fiber composite structures for motorsport and supercar applications.",
        capabilities=Capabilities(
            products=[
                Product(product_id="carbon-monocoque-296", name="Carbon Fiber Monocoque - 296 GTB",
                        category="body_chassis", subcategory="monocoque",
                        specifications={"material": "carbon_fiber_T800", "weight_kg": 98},
                        unit_price_eur=28000.00, min_order_quantity=1, lead_time_days=18),
                Product(product_id="body-panels-296", name="Body Panels Set - 296 GTB",
                        category="body_chassis", subcategory="panels",
                        specifications={"material": "carbon_fiber_composite"},
                        unit_price_eur=12000.00, min_order_quantity=1, lead_time_days=14),
            ],
            services=["custom_engineering", "prototype_development", "structural_testing"],
            production_capacity=ProductionCapacity(units_per_month=200, current_utilization_pct=85),
        ),
        identity=Identity(legal_entity="Dallara Compositi S.r.l.", registration_country="IT", vat_id="IT02345670345"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="Bureau Veritas", valid_until="2026-06-01"),
            Certification(type="ISO_9001", description="Quality Management System", issued_by="TUV Rheinland", valid_until="2026-09-15"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=44.7000, lon=10.0667, city="Varano de' Melegari", country="IT"),
            manufacturing_sites=[SiteInfo(site_id="dallara-varano", city="Varano de' Melegari", country="IT", lat=44.7000, lon=10.0667, capabilities=["layup", "autoclave", "CNC_trimming"])],
            shipping_regions=["EU"],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="EcoVadis", score=65, tier="Silver", valid_until="2026-04-01")),
        policies=Policies(payment_terms="Net 45", incoterms=["EXW", "DAP"], accepted_currencies=["EUR"],
                          insurance=InsuranceInfo(product_liability=True, max_coverage_eur=20000000), min_contract_value_eur=25000, nda_required=True),
        trust=Trust(trust_score=0.91, years_in_operation=32, ferrari_tier_status="approved_supplier", past_contracts=215, on_time_delivery_pct=93.8, defect_rate_ppm=18, dispute_count_12m=0),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/dallara-compositi-01",
                            supported_message_types=["request_quote", "negotiate", "purchase_order", "shipment_update"]),
    ))

    # 4. Magneti Marelli — Electronics
    agents.append(AgentFact(
        agent_id="magneti-marelli-01",
        name="Magneti Marelli S.p.A.",
        role="tier_1_supplier",
        description="Leading automotive electronics and powertrain component manufacturer. Part of the MARELLI group.",
        capabilities=Capabilities(
            products=[
                Product(product_id="ecu-ferrari-296", name="Engine Control Unit - 296 GTB",
                        category="electronics", subcategory="ecu",
                        specifications={"processor": "TriCore_TC397", "channels": 256},
                        unit_price_eur=4500.00, min_order_quantity=10, lead_time_days=12),
                Product(product_id="infotainment-296", name="Infotainment Head Unit",
                        category="electronics", subcategory="infotainment",
                        specifications={"display": "10.25_inch_TFT", "resolution": "1920x720"},
                        unit_price_eur=2200.00, min_order_quantity=10, lead_time_days=10),
                Product(product_id="sensor-array-296", name="Sensor Array Package",
                        category="electronics", subcategory="sensors",
                        specifications={"includes": "knock, lambda, pressure, temperature"},
                        unit_price_eur=1800.00, min_order_quantity=20, lead_time_days=8),
            ],
            services=["software_calibration", "ecu_tuning", "diagnostics_integration"],
            production_capacity=ProductionCapacity(units_per_month=50000, current_utilization_pct=68),
        ),
        identity=Identity(legal_entity="MARELLI Europe S.p.A.", registration_country="IT", vat_id="IT09396790012"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="SGS", valid_until="2026-11-01"),
            Certification(type="ISO_26262", description="Functional Safety", issued_by="TUV SUD", valid_until="2026-07-15"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=44.8015, lon=11.3264, city="Corbetta", country="IT"),
            manufacturing_sites=[SiteInfo(site_id="marelli-corbetta", city="Corbetta", country="IT", lat=45.4678, lon=8.9177, capabilities=["SMT_assembly", "testing", "firmware_flash"])],
            shipping_regions=["EU", "NA", "APAC"],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "CE_Marking", "EU_RoHS"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="EcoVadis", score=68, tier="Silver", valid_until="2026-02-01")),
        policies=Policies(payment_terms="Net 45", incoterms=["DAP", "CIF"], accepted_currencies=["EUR", "USD"],
                          insurance=InsuranceInfo(product_liability=True, max_coverage_eur=100000000)),
        trust=Trust(trust_score=0.89, years_in_operation=105, ferrari_tier_status="approved_supplier", past_contracts=1230, on_time_delivery_pct=94.5, defect_rate_ppm=22, dispute_count_12m=1),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/magneti-marelli-01",
                            supported_message_types=["request_quote", "negotiate", "purchase_order", "shipment_update"]),
    ))

    # 5. Ferrari Powertrain (Internal) — Engine/Powertrain
    agents.append(AgentFact(
        agent_id="ferrari-powertrain-internal-01",
        name="Ferrari Powertrain Division",
        role="tier_1_supplier",
        description="In-house powertrain engineering and production at Maranello. Produces the F163 hybrid V6 engine.",
        capabilities=Capabilities(
            products=[
                Product(product_id="f163-v6-engine", name="F163 2.9L Twin-Turbo V6 Engine",
                        category="powertrain", subcategory="engine",
                        specifications={"displacement_cc": 2992, "power_hp": 663, "torque_nm": 740, "hybrid": True},
                        unit_price_eur=45000.00, min_order_quantity=1, lead_time_days=10),
                Product(product_id="dct-8speed-gearbox", name="8-Speed Dual-Clutch Transmission",
                        category="powertrain", subcategory="gearbox",
                        specifications={"type": "DCT", "gears": 8, "max_torque_nm": 900},
                        unit_price_eur=18000.00, min_order_quantity=1, lead_time_days=8),
            ],
            services=["engine_assembly", "dyno_testing", "calibration"],
            production_capacity=ProductionCapacity(units_per_month=800, current_utilization_pct=78),
        ),
        identity=Identity(legal_entity="Ferrari S.p.A.", registration_country="IT", vat_id="IT00159560366"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="DNV GL", valid_until="2027-01-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=44.5294, lon=10.8633, city="Maranello", country="IT"),
            manufacturing_sites=[SiteInfo(site_id="maranello-engine", city="Maranello", country="IT", lat=44.5294, lon=10.8633, capabilities=["engine_assembly", "dyno_testing", "machining"])],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "Euro_6d", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="MSCI", score=78, tier="AA", valid_until="2026-06-01")),
        policies=Policies(payment_terms="Internal", incoterms=["EXW"]),
        trust=Trust(trust_score=1.0, years_in_operation=78, ferrari_tier_status="internal", past_contracts=0, on_time_delivery_pct=99.1, defect_rate_ppm=3),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/ferrari-powertrain-internal-01",
                            supported_message_types=["request_quote", "purchase_order"]),
    ))

    # 6. Poltrona Frau — Interior
    agents.append(AgentFact(
        agent_id="poltrona-frau-01",
        name="Poltrona Frau S.p.A.",
        role="tier_1_supplier",
        description="Luxury leather interiors supplier. Handcrafts bespoke leather seats, steering wheels, and trim for Ferrari since 1985.",
        capabilities=Capabilities(
            products=[
                Product(product_id="leather-seats-296", name="Leather Seat Assembly - 296 GTB",
                        category="interior", subcategory="seats",
                        specifications={"leather": "Poltrona_Frau_Pelle", "heating": True, "electric_adjust": True},
                        unit_price_eur=8500.00, min_order_quantity=1, lead_time_days=12),
                Product(product_id="steering-wheel-296", name="Leather Steering Wheel",
                        category="interior", subcategory="steering",
                        specifications={"diameter_mm": 360, "material": "alcantara_leather"},
                        unit_price_eur=2800.00, min_order_quantity=1, lead_time_days=8),
                Product(product_id="dashboard-module-296", name="Dashboard Module",
                        category="interior", subcategory="dashboard",
                        specifications={"material": "leather_carbon_fiber"},
                        unit_price_eur=5200.00, min_order_quantity=1, lead_time_days=10),
            ],
            services=["bespoke_customization", "color_matching", "hand_stitching"],
            production_capacity=ProductionCapacity(units_per_month=500, current_utilization_pct=80),
        ),
        identity=Identity(legal_entity="Poltrona Frau S.p.A.", registration_country="IT", vat_id="IT01045800435"),
        certifications=[
            Certification(type="ISO_9001", description="Quality Management", issued_by="Bureau Veritas", valid_until="2026-05-01"),
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="TUV Rheinland", valid_until="2026-08-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=43.3100, lon=13.4533, city="Tolentino", country="IT"),
            manufacturing_sites=[SiteInfo(site_id="pf-tolentino", city="Tolentino", country="IT", lat=43.3100, lon=13.4533, capabilities=["leather_cutting", "stitching", "assembly"])],
            shipping_regions=["EU"],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="EcoVadis", score=61, tier="Silver", valid_until="2026-03-01")),
        policies=Policies(payment_terms="Net 30", incoterms=["DAP"], accepted_currencies=["EUR"],
                          insurance=InsuranceInfo(product_liability=True, max_coverage_eur=15000000)),
        trust=Trust(trust_score=0.88, years_in_operation=112, ferrari_tier_status="approved_supplier", past_contracts=620, on_time_delivery_pct=92.1, defect_rate_ppm=8, dispute_count_12m=0),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/poltrona-frau-01",
                            supported_message_types=["request_quote", "negotiate", "purchase_order"]),
    ))

    # 7. Bilstein / Magneti Marelli — Suspension
    agents.append(AgentFact(
        agent_id="multimatic-suspension-01",
        name="Multimatic Motorsports",
        role="tier_1_supplier",
        description="Advanced suspension and damper technology. Supplies MagneRide adaptive dampers for high-performance vehicles.",
        capabilities=Capabilities(
            products=[
                Product(product_id="magneride-dampers-296", name="MagneRide Adaptive Damper Set",
                        category="suspension", subcategory="dampers",
                        specifications={"type": "magnetorheological", "positions": 4},
                        unit_price_eur=6200.00, min_order_quantity=4, lead_time_days=16),
                Product(product_id="control-arms-296", name="Forged Aluminum Control Arm Set",
                        category="suspension", subcategory="arms",
                        specifications={"material": "forged_aluminum_7075"},
                        unit_price_eur=3400.00, min_order_quantity=4, lead_time_days=12),
            ],
            services=["ride_tuning", "track_calibration", "prototype_development"],
            production_capacity=ProductionCapacity(units_per_month=3000, current_utilization_pct=74),
        ),
        identity=Identity(legal_entity="Multimatic Inc.", registration_country="CA", vat_id="CA-BN-123456789"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="BSI", valid_until="2026-10-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=42.3149, lon=-83.0364, city="Markham", country="CA"),
            manufacturing_sites=[SiteInfo(site_id="multimatic-uk", city="Thetford", country="GB", lat=52.4128, lon=0.7434, capabilities=["damper_assembly", "testing", "calibration"])],
            shipping_regions=["EU", "NA"],
        ),
        compliance=Compliance(jurisdictions=["EU", "CA", "GB"], regulations=["EU_REACH", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="EcoVadis", score=58, tier="Bronze", valid_until="2026-01-01")),
        policies=Policies(payment_terms="Net 45", incoterms=["DAP", "CIF"], accepted_currencies=["EUR", "USD", "GBP"]),
        trust=Trust(trust_score=0.86, years_in_operation=40, ferrari_tier_status="approved_supplier", past_contracts=340, on_time_delivery_pct=91.5, defect_rate_ppm=15, dispute_count_12m=0),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/multimatic-suspension-01",
                            supported_message_types=["request_quote", "negotiate", "purchase_order"]),
    ))

    # 8. OZ Racing — Wheels & Tires
    agents.append(AgentFact(
        agent_id="oz-racing-wheels-01",
        name="OZ Racing S.p.A.",
        role="tier_1_supplier",
        description="Premium forged wheel manufacturer for motorsport and luxury vehicles. Official supplier to Ferrari.",
        capabilities=Capabilities(
            products=[
                Product(product_id="forged-wheels-20", name="Forged Alloy Wheels 20-inch Set",
                        category="wheels_tires", subcategory="wheels",
                        specifications={"material": "forged_6061-T6", "diameter_inch": 20, "finish": "diamond_cut"},
                        unit_price_eur=4800.00, min_order_quantity=4, lead_time_days=10),
            ],
            services=["custom_finish", "motorsport_supply"],
            production_capacity=ProductionCapacity(units_per_month=10000, current_utilization_pct=65),
        ),
        identity=Identity(legal_entity="OZ S.p.A.", registration_country="IT", vat_id="IT00731280247"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="TUV SUD", valid_until="2026-09-01"),
            Certification(type="TUV_Wheel", description="TUV Wheel Certification", issued_by="TUV SUD", valid_until="2026-06-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=45.5764, lon=11.3508, city="San Martino di Lupari", country="IT"),
            shipping_regions=["EU", "NA", "APAC"],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="EcoVadis", score=63, tier="Silver")),
        policies=Policies(payment_terms="Net 30", incoterms=["EXW", "DAP"], accepted_currencies=["EUR"]),
        trust=Trust(trust_score=0.90, years_in_operation=53, ferrari_tier_status="approved_supplier", past_contracts=480, on_time_delivery_pct=95.3, defect_rate_ppm=5, dispute_count_12m=0),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/oz-racing-wheels-01",
                            supported_message_types=["request_quote", "negotiate", "purchase_order"]),
    ))

    # 9. Exhaust Systems — Akrapovic
    agents.append(AgentFact(
        agent_id="akrapovic-exhaust-01",
        name="Akrapovic d.d.",
        role="tier_1_supplier",
        description="Slovenian exhaust system manufacturer specializing in titanium and inconel high-performance exhaust systems.",
        capabilities=Capabilities(
            products=[
                Product(product_id="exhaust-system-296", name="Titanium Exhaust System - 296 GTB",
                        category="exhaust_emissions", subcategory="exhaust",
                        specifications={"material": "titanium_grade2", "weight_kg": 12.5, "db_limit": 90},
                        unit_price_eur=8900.00, min_order_quantity=1, lead_time_days=14),
            ],
            services=["custom_tuning", "sound_engineering"],
            production_capacity=ProductionCapacity(units_per_month=5000, current_utilization_pct=70),
        ),
        identity=Identity(legal_entity="Akrapovic d.d.", registration_country="SI", vat_id="SI48233757"),
        certifications=[
            Certification(type="IATF_16949", description="Automotive Quality Management", issued_by="SIQ", valid_until="2026-04-01"),
            Certification(type="ISO_14001", description="Environmental Management", issued_by="SIQ", valid_until="2026-07-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=45.9517, lon=14.8064, city="Ivancna Gorica", country="SI"),
            shipping_regions=["EU", "NA"],
        ),
        compliance=Compliance(jurisdictions=["EU", "SI"], regulations=["EU_REACH", "Euro_6d", "CE_Marking"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="EcoVadis", score=66, tier="Silver")),
        policies=Policies(payment_terms="Net 30", incoterms=["DAP", "EXW"], accepted_currencies=["EUR"]),
        trust=Trust(trust_score=0.87, years_in_operation=34, ferrari_tier_status="approved_supplier", past_contracts=180, on_time_delivery_pct=94.8, defect_rate_ppm=10, dispute_count_12m=0),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/akrapovic-exhaust-01",
                            supported_message_types=["request_quote", "negotiate", "purchase_order"]),
    ))

    # 10. DHL Logistics
    agents.append(AgentFact(
        agent_id="dhl-logistics-01",
        name="DHL Supply Chain Italy",
        role="logistics_provider",
        description="Global logistics provider offering dedicated automotive supply chain solutions across Europe.",
        capabilities=Capabilities(
            services=["road_freight", "express_delivery", "warehousing", "customs_clearance", "insurance"],
            production_capacity=ProductionCapacity(units_per_month=100000, current_utilization_pct=55),
        ),
        identity=Identity(legal_entity="DHL Supply Chain (Italy) S.p.A.", registration_country="IT", vat_id="IT12580090158"),
        certifications=[
            Certification(type="ISO_9001", description="Quality Management", issued_by="Lloyd's Register", valid_until="2026-12-01"),
            Certification(type="AEO", description="Authorized Economic Operator", issued_by="EU Customs", valid_until="2026-06-01"),
        ],
        location=LocationInfo(
            headquarters=Location(lat=45.4654, lon=9.1859, city="Milan", country="IT"),
            shipping_regions=["EU", "NA", "APAC", "ME", "AF"],
        ),
        compliance=Compliance(jurisdictions=["EU", "IT"], regulations=["EU_REACH", "ADR_Transport"], sanctions_clear=True,
                              esg_rating=ESGRating(provider="CDP", score=75, tier="A-")),
        policies=Policies(payment_terms="Net 30", incoterms=["DAP", "DDP", "CIF"], accepted_currencies=["EUR", "USD", "GBP"]),
        trust=Trust(trust_score=0.92, years_in_operation=55, ferrari_tier_status="approved_provider", past_contracts=2100, on_time_delivery_pct=97.1, defect_rate_ppm=2, dispute_count_12m=0),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/dhl-logistics-01",
                            supported_message_types=["logistics_request", "shipment_update"]),
    ))

    # 11. Compliance Agent
    agents.append(AgentFact(
        agent_id="eu-compliance-agent-01",
        name="EU Compliance Validator",
        role="compliance_agent",
        description="Automated compliance validation service. Checks certifications, sanctions, ESG scores, and regulatory compliance for all supply chain actors.",
        capabilities=Capabilities(
            services=["certification_validity", "sanctions_screening", "esg_threshold", "regulation_compliance"],
        ),
        identity=Identity(legal_entity="SupplyGuard GmbH", registration_country="DE"),
        location=LocationInfo(
            headquarters=Location(lat=50.1109, lon=8.6821, city="Frankfurt", country="DE"),
        ),
        compliance=Compliance(jurisdictions=["EU"], regulations=["EU_REACH", "EU_ELV_Directive", "CE_Marking", "EU_RoHS"]),
        trust=Trust(trust_score=0.95, years_in_operation=12, ferrari_tier_status="approved_provider", past_contracts=5400),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/eu-compliance-agent-01",
                            supported_message_types=["compliance_check", "compliance_result"]),
    ))

    # 12. Assembly Coordinator
    agents.append(AgentFact(
        agent_id="maranello-assembly-01",
        name="Maranello Assembly Coordinator",
        role="assembly_coordinator",
        description="Manages BOM validation, assembly sequencing, and delivery scheduling at the Maranello plant.",
        capabilities=Capabilities(
            services=["bom_management", "assembly_sequencing", "delivery_scheduling", "quality_control"],
        ),
        identity=Identity(legal_entity="Ferrari S.p.A.", registration_country="IT"),
        location=LocationInfo(
            headquarters=Location(lat=44.5294, lon=10.8633, city="Maranello", country="IT"),
        ),
        trust=Trust(trust_score=1.0, years_in_operation=78, ferrari_tier_status="internal"),
        network=NetworkInfo(endpoint="http://localhost:8000/agent/maranello-assembly-01",
                            supported_message_types=["purchase_order", "order_confirmation", "shipment_update"]),
    ))

    # 13. Disqualified agents (for realism)
    agents.append(AgentFact(
        agent_id="cheapparts-cn-03",
        name="CheapParts Shenzhen Ltd.",
        role="tier_1_supplier",
        description="Low-cost brake component manufacturer.",
        capabilities=Capabilities(
            products=[
                Product(product_id="generic-brake-disc", name="Steel Brake Disc 380mm", category="braking_system",
                        unit_price_eur=180.00, min_order_quantity=500, lead_time_days=30),
            ],
        ),
        identity=Identity(legal_entity="CheapParts Ltd.", registration_country="CN"),
        certifications=[
            Certification(type="ISO_9001", description="Quality Management", issued_by="Local", valid_until="2025-01-01", status="expired"),
        ],
        location=LocationInfo(headquarters=Location(lat=22.5431, lon=114.0579, city="Shenzhen", country="CN")),
        compliance=Compliance(jurisdictions=["CN"], regulations=[], sanctions_clear=True,
                              esg_rating=ESGRating(provider="Self-assessed", score=35, tier="None")),
        trust=Trust(trust_score=0.31, years_in_operation=4, ferrari_tier_status="not_approved", past_contracts=12, on_time_delivery_pct=72.0, defect_rate_ppm=340, dispute_count_12m=5),
    ))

    agents.append(AgentFact(
        agent_id="noname-logistics-07",
        name="NoName Freight Co.",
        role="logistics_provider",
        description="Small regional freight company.",
        capabilities=Capabilities(services=["road_freight"]),
        identity=Identity(legal_entity="NoName Freight", registration_country="RO"),
        location=LocationInfo(headquarters=Location(lat=44.4268, lon=26.1025, city="Bucharest", country="RO")),
        trust=Trust(trust_score=0.31, years_in_operation=2, ferrari_tier_status="not_approved", past_contracts=8, on_time_delivery_pct=68.0),
    ))

    return agents


# ── Category-to-Agent mapping for quick lookup ──────────────────────────────

CATEGORY_AGENT_MAP = {
    "powertrain": "ferrari-powertrain-internal-01",
    "braking_system": "brembo-brake-supplier-01",
    "body_chassis": "dallara-compositi-01",
    "electronics": "magneti-marelli-01",
    "interior": "poltrona-frau-01",
    "suspension": "multimatic-suspension-01",
    "wheels_tires": "oz-racing-wheels-01",
    "exhaust_emissions": "akrapovic-exhaust-01",
}
