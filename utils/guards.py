"""Page guards: put one at the top of any page that needs a signed-in user or a role (US-MGT-01, US-CHK-01).

This is layer 2 of 3 (NFR-ROLE-02): the menu hides the page, this guard stops the page if someone
opens its URL directly, and the database security rules (supabase/migrations/0005) are the real lock.
"""

from __future__ import annotations

import streamlit as st

from components.states import access_denied
from models.user import UserProfile
from services.auth import current_user

SIGN_IN_PAGE = "app_pages/sign_in.py"
REGISTER_PAGE = "app_pages/register.py"
RETURN_TO_KEY = "return_to"


def require_signed_in(message: str = "Sign in to continue.", *, return_to: str | None = None) -> UserProfile:
    """Returns the signed-in user, or shows a sign-in panel and stops the page.

    `return_to` is the page to come back to after signing in, for example "app_pages/checkout.py"
    (US-CART-04: the cart is kept, and the shopper lands back where they were).
    """
    user = current_user()
    if user is None:
        if return_to:
            st.session_state[RETURN_TO_KEY] = return_to
        with st.container(border=True, key="sign_in_gate"):
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
        access_denied("Owner only" if roles == ("owner",) else "Staff access only")
        st.stop()
    return user
