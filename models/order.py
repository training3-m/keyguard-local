"""An order and its lines, as shown on My orders, the confirmation and the Manage pages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ORDER_STATUSES = ("Placed", "Packed", "Shipped", "Cancelled")


@dataclass(frozen=True)
class OrderLine:
    """One line of an order. Name and price were frozen when the order was placed."""

    sku: str
    product_name: str
    unit_price_cents: int
    qty: int
    line_total_cents: int
    community_gift_cents: int = 0

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> OrderLine:
        """Builds an OrderLine from a public.order_items row."""
        return cls(
            sku=str(row["sku"]),
            product_name=str(row["product_name"]),
            unit_price_cents=int(row["unit_price_cents"]),
            qty=int(row["qty"]),
            line_total_cents=int(row["line_total_cents"]),
            community_gift_cents=int(row.get("community_gift_cents") or 0),
        )


@dataclass(frozen=True)
class Order:
    """One demo order (public.orders) with its lines."""

    order_number: str
    status: str
    customer_name: str
    customer_email: str
    subtotal_cents: int
    shipping_cents: int
    tax_cents: int
    total_cents: int
    community_gift_cents: int
    created_at: str
    email_file: str | None = None
    lines: list[OrderLine] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Order:
        """Builds an Order from a public.orders row; lines come from a nested "order_items" list if present."""
        return cls(
            order_number=str(row["order_number"]),
            status=str(row["status"]),
            customer_name=str(row["customer_name"]),
            customer_email=str(row["customer_email"]),
            subtotal_cents=int(row["subtotal_cents"]),
            shipping_cents=int(row["shipping_cents"]),
            tax_cents=int(row["tax_cents"]),
            total_cents=int(row["total_cents"]),
            community_gift_cents=int(row.get("community_gift_cents") or 0),
            created_at=str(row["created_at"]),
            email_file=row.get("email_file"),
            lines=[OrderLine.from_row(item) for item in row.get("order_items") or []],
        )
