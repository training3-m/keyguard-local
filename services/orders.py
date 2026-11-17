"""Checkout and the customer's own orders. Owner: User 2.

Placing an order always goes through the database function public.place_order (0007), which checks
stock, recalculates prices and lowers stock in one transaction. Never insert orders directly.
Keep every name and parameter; fill in the bodies in the stories listed.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from models.order import Order


def place_order(cart: dict[str, int], shipping: dict[str, str], idempotency_key: UUID) -> dict[str, Any]:
    """Calls public.place_order. `shipping` has full_name, address, city, zip.

    Returns the database result (order_number, totals, already_placed). Raises a friendly error when
    stock ran out or a field is invalid (US-CHK-02, US-CHK-03, U2-03).
    """
    raise NotImplementedError("US-CHK-02: place_order (U2-03)")


def get_order(order_number: str) -> Order | None:
    """One order with its lines, if the signed-in user may see it (confirmation page, US-CHK-05, U2-04)."""
    raise NotImplementedError("US-CHK-05: get_order (U2-04)")


def list_my_orders() -> list[Order]:
    """The signed-in customer's own orders, newest first (US-CHK-06, U2-08)."""
    raise NotImplementedError("US-CHK-06: list_my_orders (U2-08)")


def record_email_file(order_number: str, path: str) -> None:
    """Saves where the .eml confirmation was written, via public.set_order_email_file (US-CHK-04, U2-05)."""
    raise NotImplementedError("US-CHK-04: record_email_file (U2-05)")
