"""The owner's Staff & Users page. Owner: User 1.

Roles change only through public.set_user_role (0008), which allows customer <-> staff, never "owner",
and never on yourself. Keep every name and parameter.
"""

from __future__ import annotations

from models.user import UserProfile


def list_users(term: str = "") -> list[UserProfile]:
    """All accounts with name and role, filtered by email or name (US-MGT-10, U1-05)."""
    raise NotImplementedError("US-MGT-10: list_users (U1-05)")


def set_user_role(user_id: str, role: str) -> None:
    """Makes someone staff, or back to customer, via public.set_user_role (US-MGT-10, U1-05)."""
    raise NotImplementedError("US-MGT-10: set_user_role (U1-05)")
