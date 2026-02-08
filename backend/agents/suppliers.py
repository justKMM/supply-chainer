from __future__ import annotations

from backend.schemas import (
    AgentFact,
    Capabilities,
    Certification,
    Compliance,
    ESGRating,
    Identity,
    InsuranceInfo,
    Location,
    LocationInfo,
    NetworkInfo,
    Policies,
    Product,
    ProductionCapacity,
    SiteInfo,
    Trust,
    UpstreamDependency,
)


def supplier_agents() -> list[AgentFact]:
    agents: list[AgentFact] = []

    # Brembo — Brakes
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

    # Dallara Compositi — Body/Chassis
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

    # Magneti Marelli — Electronics
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

    # Poltrona Frau — Interior
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

    # Bilstein / Magneti Marelli — Suspension
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

    # OZ Racing — Wheels & Tires
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

    # Exhaust Systems — Akrapovic
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

    return agents
