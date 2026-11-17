"""My Account > Profile tab: edit name and change password.

Owner: User 1, story US-AUTH-04 (pick code U1-07). Keep the function name and parameters.
"""

from __future__ import annotations

from components.states import coming_soon
from models.user import UserProfile


def render_account_profile(user: UserProfile) -> None:
    """Shows the Profile tab for the signed-in user (02-ui-ux.md §4.8)."""
    coming_soon("US-AUTH-04 · U1-07", "edit your name and change your password")
