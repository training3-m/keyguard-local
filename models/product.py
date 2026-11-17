"""A product (drive or accessory) as the app uses it. Matches public.products (0002_products.sql)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

LOW_STOCK_THRESHOLD = 5  # "Only N left" and the dashboard low-stock list (01-product.md §A6)


@dataclass(frozen=True)
class Product:
    """One row of public.products. Money is in cents."""

    id: int
    sku: str
    name: str
    category: str
    price_cents: int
    stock_qty: int
    community_gift_cents: int = 0
    capacity_gb: int | None = None
    color: str | None = None
    description: str | None = None
    specs: dict[str, Any] = field(default_factory=dict)
    image_url: str | None = None
    is_active: bool = True
    featured_rank: int = 100

    @property
    def in_stock(self) -> bool:
        """True if at least one can be bought."""
        return self.is_active and self.stock_qty > 0

    @property
    def low_stock(self) -> bool:
        """True when only a few are left (1 to 5)."""
        return 0 < self.stock_qty <= LOW_STOCK_THRESHOLD

    @property
    def max_order_qty(self) -> int:
        """Most a shopper may put in the cart: 10, or less if stock is lower (01-product.md §A6)."""
        return max(0, min(10, self.stock_qty))

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Product:
        """Builds a Product from a Supabase row (extra columns are ignored)."""
        return cls(
            id=int(row["id"]),
            sku=str(row["sku"]),
            name=str(row["name"]),
            category=str(row["category"]),
            price_cents=int(row["price_cents"]),
            stock_qty=int(row["stock_qty"]),
            community_gift_cents=int(row.get("community_gift_cents") or 0),
            capacity_gb=row.get("capacity_gb"),
            color=row.get("color"),
            description=row.get("description"),
            specs=dict(row.get("specs") or {}),
            image_url=row.get("image_url"),
            is_active=bool(row.get("is_active", True)),
            featured_rank=int(row.get("featured_rank") or 100),
        )
