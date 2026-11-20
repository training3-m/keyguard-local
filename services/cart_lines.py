"""Turning the session cart {sku: qty} into lines with CURRENT prices and stock. Owner: User 2.

Prices are always read fresh from the database, never kept in the session (US-CART-02 AC2).
Keep the name and parameters; fill in the body in the story listed.
"""

from __future__ import annotations

from typing import Any

from models.cart import CartLine
from services import supabase_client

# Only the columns the cart needs.
_COLUMNS = "sku, name, price_cents, community_gift_cents, stock_qty, is_active, image_url"


def load_cart_lines(cart: dict[str, int]) -> list[CartLine]:
    """One CartLine per product in the cart, with today's price, gift, stock and active flag.

    Products that no longer exist are left out; the cart page warns about them (US-CART-02 AC3, U2-01).
    Guests can't read hidden products (0005), so for them a hidden drive is "no longer exists" too.
    Not cached on purpose: the cart must show the price and stock of right now.
    """
    if not cart:
        return []

    result = (
        supabase_client.get_client()
        .table("products")
        .select(_COLUMNS)
        .in_("sku", list(cart))
        .execute()
    )
    rows: dict[str, dict[str, Any]] = {
        str(row["sku"]): dict(row) for row in (result.data or []) if isinstance(row, dict)
    }

    lines = []
    for sku, qty in cart.items():  # keep the order the shopper added things in
        row = rows.get(sku)
        if row is None:
            continue
        lines.append(CartLine(
            sku=sku,
            name=str(row["name"]),
            unit_price_cents=int(row["price_cents"]),
            qty=int(qty),
            community_gift_cents=int(row.get("community_gift_cents") or 0),
            stock_qty=int(row.get("stock_qty") or 0),
            is_active=bool(row.get("is_active", True)),
            image_url=row.get("image_url"),
        ))
    return lines
