"""Owner > Staff & users (S14). Owner only. Owner: User 1.

Story: US-MGT-10 (U1-05). Use services.users. Every role change needs a confirmation dialog (UX-10).
"""

from components.states import coming_soon
from utils.guards import require_role

user = require_role("owner")

coming_soon("US-MGT-10 · U1-05", "promote a customer to staff, or back")
