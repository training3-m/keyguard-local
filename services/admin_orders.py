"""Managing orders (staff and owner). Owner: User 3.

Staff move orders Placed -> Packed -> Shipped. Only the owner cancels, through public.cancel_order (0008),
which also puts the stock back. Keep every name and parameter.
"""

from __future__ import annotations

from datetime import date

from models.order import Order


def list_orders(status: str | None = None, date_from: date | None = None,
                date_to: date | None = None) -> list[Order]:
    """All orders with their lines, newest first, optionally filtered (US-MGT-09, U3-07)."""
    raise NotImplementedError("US-MGT-09: list_orders (U3-07)")


def set_status(order_number: str, status: str) -> None:
    """Moves an order to Packed or Shipped; the database refuses other changes (US-MGT-09, U3-07)."""
    raise NotImplementedError("US-MGT-09: set_status (U3-07)")


def cancel_order(order_number: str) -> None:
    """Owner only: cancels via public.cancel_order, which restocks the items (US-MGT-09 AC3, U3-07)."""
    raise NotImplementedError("US-MGT-09: cancel_order (U3-07)")
