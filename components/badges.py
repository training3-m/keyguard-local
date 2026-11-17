"""Small labels used on cards, pages and tables. Every badge has text, never color alone (02 §6)."""

from __future__ import annotations

from typing import Literal

import streamlit as st

from models.product import LOW_STOCK_THRESHOLD
from utils.formatting import money

BadgeColor = Literal["red", "orange", "yellow", "blue", "green", "violet", "gray", "primary"]

_STATUS_STYLE: dict[str, tuple[BadgeColor, str]] = {
    "Placed": ("blue", ":material/receipt_long:"),
    "Packed": ("violet", ":material/inventory_2:"),
    "Shipped": ("green", ":material/local_shipping:"),
    "Cancelled": ("gray", ":material/cancel:"),
}


def stock_badge(stock_qty: int, *, is_active: bool = True) -> None:
    """In stock (green), Only N left (orange, 5 or fewer) or Out of stock (red). Shows REAL stock only."""
    if not is_active or stock_qty <= 0:
        st.badge("Out of stock", color="red", icon=":material/remove_shopping_cart:")
    elif stock_qty <= LOW_STOCK_THRESHOLD:
        st.badge(f"Only {stock_qty} left", color="orange", icon=":material/warning:")
    else:
        st.badge("In stock", color="green", icon=":material/check_circle:")


def order_status_badge(status: str) -> None:
    """Placed, Packed, Shipped or Cancelled, each with its own icon."""
    color, icon = _STATUS_STYLE.get(status, ("gray", ":material/help:"))
    st.badge(status, color=color, icon=icon)


def role_badge(role: str) -> None:
    """CUSTOMER, STAFF or OWNER, shown next to the signed-in name."""
    st.badge(role.upper(), color="violet" if role in ("staff", "owner") else "blue",
             icon=":material/badge:")


def community_chip(gift_cents: int) -> None:
    """How much goes to the Rancho Library fund, for example "$3.00 to Rancho Library"."""
    if gift_cents > 0:
        st.badge(f"{money(gift_cents)} to Rancho Library", color="green",
                 icon=":material/volunteer_activism:")


def security_strip() -> None:
    """The three security features on every product card (UX-03)."""
    with st.container(horizontal=True, gap="small"):
        st.badge("PIN keypad", color="violet", icon=":material/dialpad:")
        st.badge("AES-256", color="violet", icon=":material/shield:")
        st.badge("Auto-wipe", color="violet", icon=":material/delete_forever:")
