"""Page guards: put one at the top of any page that needs a signed-in user or a role.

This is layer 2 of 3 (NFR-ROLE-02): the menu hides the page, this guard stops the page if someone
opens its URL directly, and the database security rules (supabase/migrations/0005) are the real lock.
"""

from __future__ import annotations

import streamlit as st

from models.user import UserProfile
from services.auth import current_user

SIGN_IN_PAGE = "app_pages/sign_in.py"
REGISTER_PAGE = "app_pages/register.py"


def require_signed_in(message: str = "Sign in to continue.") -> UserProfile:
    """Returns the signed-in user, or shows a sign-in prompt and stops the page."""
    user = current_user()
    if user is None:
        with st.container(border=True):
            st.markdown(f":material/lock: **{message}**")
            with st.container(horizontal=True):
                st.page_link(SIGN_IN_PAGE, label="Sign in", icon=":material/login:")
                st.page_link(REGISTER_PAGE, label="Create account", icon=":material/person_add:")
        st.stop()
    return user


def require_role(*roles: str) -> UserProfile:
    """Returns the user if their role is one of `roles`; otherwise shows "access denied" and stops."""
    user = require_signed_in()
    if user.role not in roles:
        label = "Owner only" if roles == ("owner",) else "Staff access only"
        st.error("This page isn't available for your account.", title=label, icon=":material/block:")
        st.page_link("app_pages/shop.py", label="Go to shop", icon=":material/storefront:")
        st.stop()
    return user
