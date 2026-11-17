"""Numbers for the Manage dashboard (staff and owner). Owner: User 2.

Staff see orders, units sold, low stock and recent orders. Revenue and community totals are owner only
(US-MGT-08 AC2): don't return them for staff. Keep every name and parameter.
"""

from __future__ import annotations

from models.order import Order
from models.product import Product


def metrics(role: str) -> dict[str, int]:
    """Totals for the metric tiles: orders, units_sold, and for the owner revenue_cents and community_cents."""
    raise NotImplementedError("US-MGT-08: metrics (U2-06)")


def low_stock(threshold: int = 5) -> list[Product]:
    """Active products with stock at or below `threshold` (US-MGT-08 AC1, U2-06)."""
    raise NotImplementedError("US-MGT-08: low_stock (U2-06)")


def recent_orders(limit: int = 10) -> list[Order]:
    """The newest orders (US-MGT-08 AC1, U2-06)."""
    raise NotImplementedError("US-MGT-08: recent_orders (U2-06)")
