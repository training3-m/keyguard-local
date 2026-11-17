"""Standard messages for empty, error, access-denied and not-built-yet screens (02-ui-ux.md §13)."""

from __future__ import annotations

import streamlit as st


def coming_soon(story_id: str, what: str) -> None:
    """Placeholder for a page part a story will build, for example coming_soon("US-CART-02", "the cart")."""
    st.info(f"Coming soon: {what}.", title=story_id, icon=":material/construction:")


def empty_state(message: str, *, icon: str = ":material/inbox:", action_label: str | None = None,
                action_page: str | None = None) -> None:
    """An icon, one sentence and at most one action, for example "Your cart is empty. Browse drives"."""
    with st.container(border=True):
        st.markdown(f"{icon} {message}")
        if action_label and action_page:
            st.page_link(action_page, label=action_label, icon=":material/arrow_forward:")


def error_state(message: str = "Something went wrong. Please try again.", *, key: str) -> bool:
    """A friendly error with a "Try again" button. Returns True when the button is clicked.

    Never pass raw database errors here: details belong in the server log (NFR-SEC-08).
    """
    st.error(message, icon=":material/error:")
    return st.button("Try again", key=key, icon=":material/refresh:")


def access_denied(title: str = "Staff access only") -> None:
    """Shown when someone opens a page their role can't use (02-ui-ux.md §13)."""
    st.error("This page isn't available for your account.", title=title, icon=":material/block:")
    st.page_link("app_pages/shop.py", label="Go to shop", icon=":material/storefront:")


def not_found(what: str = "Product") -> None:
    """For an unknown or hidden SKU or order number (US-PDP-01 AC2)."""
    st.warning(f"{what} not found.", icon=":material/search_off:")
    st.page_link("app_pages/shop.py", label="Back to shop", icon=":material/arrow_back:")


def store_unavailable() -> None:
    """Full-page message when the database can't be reached (NFR-REL-03)."""
    st.error("The store is temporarily unavailable. Please try again in a minute.",
             title="Store unavailable", icon=":material/cloud_off:")
