"""My Account > My orders tab: the signed-in customer's own orders.

Owner: User 2, story US-CHK-06 (pick code U2-08). Keep the function name and parameters.
Use services.orders.list_my_orders() and components.order_detail.order_detail().
"""

from __future__ import annotations

from components.states import coming_soon
from models.user import UserProfile


def render_my_orders(user: UserProfile) -> None:
    """Shows the My orders tab for the signed-in user (02-ui-ux.md §4.8)."""
    coming_soon("US-CHK-06 · U2-08", "your past orders and their confirmation emails")
