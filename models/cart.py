"""A cart line and the cart totals. Money is in cents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CartLine:
    """One product in the cart, with its CURRENT database price (US-CART-02 AC2)."""

    sku: str
    name: str
    unit_price_cents: int
    qty: int
    community_gift_cents: int = 0  # per unit
    stock_qty: int = 0
    is_active: bool = True

    @property
    def line_total_cents(self) -> int:
        """Price x quantity."""
        return self.unit_price_cents * self.qty

    @property
    def gift_total_cents(self) -> int:
        """Community gift for this line (gift per unit x quantity)."""
        return self.community_gift_cents * self.qty


@dataclass(frozen=True)
class Totals:
    """Everything the cart, checkout and confirmation show at the bottom."""

    subtotal_cents: int
    shipping_cents: int
    tax_cents: int
    total_cents: int
    community_gift_cents: int
    free_shipping_gap_cents: int  # how much more to spend for free shipping; 0 if already free
