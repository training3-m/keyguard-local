"""Checkout and the customer's own orders. Owner: User 2.

Placing an order always goes through the database function public.place_order (0007), which checks
stock, recalculates prices and lowers stock in one transaction. Never insert orders directly.
Keep every name and parameter; fill in the bodies in the stories listed.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from postgrest.exceptions import APIError

from models.order import Order
from services import supabase_client

logger = logging.getLogger(__name__)

# Postgres error codes that place_order (0007) raises ON PURPOSE, with a message written for
# shoppers. Any other error is unexpected, so its details stay in the server log (NFR-SEC-08).
_FRIENDLY_CODES = {
    "22023",  # invalid_parameter_value: a field or item is wrong
    "23514",  # check_violation: not enough stock
    "42501",  # insufficient_privilege: not signed in
}
_OUT_OF_STOCK_CODE = "23514"
GENERIC_ORDER_ERROR = "We couldn't place your order right now. Please try again in a minute."


class OrderError(Exception):
    """An order that could not be placed, with a message that is safe to show the shopper.

    `out_of_stock` is True when stock ran out, so the page can send the shopper back to the cart
    (US-CHK-03 AC2).
    """

    def __init__(self, message: str, *, out_of_stock: bool = False):
        super().__init__(message)
        self.message = message
        self.out_of_stock = out_of_stock


def place_order(cart: dict[str, int], shipping: dict[str, str], idempotency_key: UUID) -> dict[str, Any]:
    """Calls public.place_order. `shipping` has full_name, address, city, zip.

    Returns the database result (order_number, totals, already_placed). Raises a friendly error when
    stock ran out or a field is invalid (US-CHK-02, US-CHK-03, U2-03).

    Only SKUs and quantities are sent: the database looks up prices itself, so a changed price in
    the browser can never change what the order costs. Everything happens in ONE transaction there.
    """
    items = [{"sku": sku, "qty": qty} for sku, qty in cart.items()]
    try:
        result = supabase_client.get_client().rpc("place_order", {
            "p_items": items,
            "p_shipping": {key: shipping.get(key, "").strip()
                           for key in ("full_name", "address", "city", "zip")},
            "p_idempotency_key": str(idempotency_key),
        }).execute()
    except APIError as error:
        if error.code in _FRIENDLY_CODES and error.message:
            raise OrderError(error.message, out_of_stock=error.code == _OUT_OF_STOCK_CODE) from None
        logger.exception("place_order failed unexpectedly")
        raise OrderError(GENERIC_ORDER_ERROR) from None
    except Exception:  # network trouble and the like
        logger.exception("place_order failed unexpectedly")
        raise OrderError(GENERIC_ORDER_ERROR) from None

    data = result.data
    if not isinstance(data, dict) or "order_number" not in data:
        logger.error("place_order returned something unexpected")
        raise OrderError(GENERIC_ORDER_ERROR)
    return dict(data)


def get_order(order_number: str) -> Order | None:
    """One order with its lines, if the signed-in user may see it (confirmation page, US-CHK-05, U2-04)."""
    raise NotImplementedError("US-CHK-05: get_order (U2-04)")


def list_my_orders() -> list[Order]:
    """The signed-in customer's own orders, newest first (US-CHK-06, U2-08)."""
    raise NotImplementedError("US-CHK-06: list_my_orders (U2-08)")


def record_email_file(order_number: str, path: str) -> None:
    """Saves where the .eml confirmation was written, via public.set_order_email_file (US-CHK-04, U2-05)."""
    raise NotImplementedError("US-CHK-04: record_email_file (U2-05)")
