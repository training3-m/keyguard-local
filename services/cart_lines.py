"""Turning the session cart {sku: qty} into lines with CURRENT prices and stock. Owner: User 2.

Prices are always read fresh from the database, never kept in the session (US-CART-02 AC2).
Keep the name and parameters; fill in the body in the story listed.
"""

from __future__ import annotations

from models.cart import CartLine


def load_cart_lines(cart: dict[str, int]) -> list[CartLine]:
    """One CartLine per product in the cart, with today's price, gift, stock and active flag.

    Products that no longer exist are left out; the cart page warns about them (US-CART-02 AC3, U2-01).
    """
    raise NotImplementedError("US-CART-02: load_cart_lines (U2-01)")
