"""Manage > Orders (S13). Staff and owner. Owner: User 3.

Story: US-MGT-09 (U3-07). Use services.admin_orders and components.order_detail.
Staff: Placed -> Packed -> Shipped. Only the owner sees Cancel order.
"""

from components.states import coming_soon
from utils.guards import require_role

user = require_role("staff", "owner")

coming_soon("US-MGT-09 · U3-07", "all orders, their details, and status changes"
            + (", including cancel" if user.is_owner else ""))
