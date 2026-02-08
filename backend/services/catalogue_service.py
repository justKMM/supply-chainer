"""Product catalogue service — in-memory catalogue of Ferrari models for employee selection."""

from __future__ import annotations

from backend.schemas import CatalogueProduct


# ── Seed Catalogue ────────────────────────────────────────────────────────────

DEFAULT_CATALOGUE: list[CatalogueProduct] = [
    CatalogueProduct(
        product_id="ferrari-296-gtb",
        name="Ferrari 296 GTB",
        description="Hybrid V6 supercar — 830 cv, 0-100 km/h in 2.9s",
        selling_price_eur=330_000.0,
        intent_template="Buy all parts required to assemble one {name}",
        currency="EUR",
    ),
    CatalogueProduct(
        product_id="ferrari-sf90-stradale",
        name="Ferrari SF90 Stradale",
        description="Plug-in hybrid V8 — 1000 cv, Ferrari's most powerful road car",
        selling_price_eur=500_000.0,
        intent_template="Buy all parts required to assemble one {name}",
        currency="EUR",
    ),
    CatalogueProduct(
        product_id="ferrari-roma",
        name="Ferrari Roma",
        description="Front-engined V8 GT — 620 cv, grand touring elegance",
        selling_price_eur=250_000.0,
        intent_template="Buy all parts required to assemble one {name}",
        currency="EUR",
    ),
    CatalogueProduct(
        product_id="ferrari-purosangue",
        name="Ferrari Purosangue",
        description="First Ferrari SUV — V12 naturally aspirated, four doors",
        selling_price_eur=390_000.0,
        intent_template="Buy all parts required to assemble one {name}",
        currency="EUR",
    ),
]


class CatalogueService:
    """In-memory product catalogue."""

    def __init__(self):
        self._products: dict[str, CatalogueProduct] = {p.product_id: p for p in DEFAULT_CATALOGUE}

    def list_all(self) -> list[CatalogueProduct]:
        return list(self._products.values())

    def get(self, product_id: str) -> CatalogueProduct | None:
        return self._products.get(product_id)

    def get_intent_for_product(self, product: CatalogueProduct, quantity: int) -> str:
        """Build procurement intent from product and quantity."""
        if quantity == 1:
            return product.intent_template.format(name=product.name)
        return f"Buy all parts required to assemble {quantity} {product.name}"


# Global singleton
catalogue_service = CatalogueService()
