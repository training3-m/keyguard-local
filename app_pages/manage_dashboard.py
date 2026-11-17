"""Manage > Dashboard (S10). Staff and owner. Owner: User 2.

Story: US-MGT-08 (U2-06). Use services.dashboard. Revenue and community tiles are owner only.
"""

from components.states import coming_soon
from utils.guards import require_role

user = require_role("staff", "owner")

coming_soon("US-MGT-08 · U2-06", "orders, units sold, low stock and recent orders"
            + (", plus revenue and community totals" if user.is_owner else ""))
