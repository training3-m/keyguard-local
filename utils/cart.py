"""The shopping cart, kept in this browser session as {sku: quantity} (US-CART-01 AC4).

Everyone (guests included) can use the cart. It survives page changes and signing in or out
(US-CART-04). Prices are NOT stored here: they are always read fresh from the database.
"""

from __future__ import annotations

import streamlit as st

MAX_PER_LINE = 10  # 01-product.md §A6
_CART_KEY = "cart"


def get_cart() -> dict[str, int]:
    """The cart as {sku: quantity}. Creates an empty cart the first time."""
    if _CART_KEY not in st.session_state:
        st.session_state[_CART_KEY] = {}
    return st.session_state[_CART_KEY]


def add(sku: str, qty: int = 1, max_qty: int = MAX_PER_LINE) -> int:
    """Adds `qty` of a product, never going above `max_qty` (10 or the stock). Returns the new quantity."""
    cart = get_cart()
    limit = min(max_qty, MAX_PER_LINE)
    new_qty = max(0, min(cart.get(sku, 0) + qty, limit))
    if new_qty == 0:
        cart.pop(sku, None)
    else:
        cart[sku] = new_qty
    return new_qty


def update(sku: str, qty: int, max_qty: int = MAX_PER_LINE) -> int:
    """Sets a product's quantity (0 or less removes it), capped at `max_qty`. Returns the new quantity."""
    cart = get_cart()
    new_qty = max(0, min(qty, max_qty, MAX_PER_LINE))
    if new_qty == 0:
        cart.pop(sku, None)
    else:
        cart[sku] = new_qty
    return new_qty


def remove(sku: str) -> None:
    """Takes a product out of the cart."""
    get_cart().pop(sku, None)


def clear() -> None:
    """Empties the cart (after a successful order, US-CHK-05 AC2)."""
    st.session_state[_CART_KEY] = {}


def count() -> int:
    """Total number of items, for the cart badge in the menu (02-ui-ux.md §2.3)."""
    return sum(get_cart().values())
