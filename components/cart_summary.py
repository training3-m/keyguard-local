"""The totals box shown under the cart, and later on checkout (02-ui-ux.md §4.4). Owner: User 2.

Stories: US-CART-02 (U2-01) builds the box; US-CART-03 (U2-07) adds the free-shipping hint.
"""

from __future__ import annotations

import streamlit as st

from models.cart import Totals
from utils.formatting import money


def _row(label: str, value: str, *, bold: bool = False) -> None:
    """One line of the box: the label on the left, the amount on the right."""
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.markdown(f"**{label}**" if bold else label)
        st.markdown(f"**{value}**" if bold else value)


def cart_summary(totals: Totals) -> None:
    """Subtotal, shipping, tax, total and the gift to the Rancho Library fund."""
    with st.container(border=True, key="cart_summary"):
        _row("Subtotal", money(totals.subtotal_cents))
        _row("Shipping", "FREE" if totals.shipping_cents == 0 else money(totals.shipping_cents))
        _row("Tax (8%)", money(totals.tax_cents))
        _row("Total", money(totals.total_cents), bold=True)
        if totals.community_gift_cents > 0:
            _row(":material/volunteer_activism: To Rancho Library", money(totals.community_gift_cents))
        st.caption("Demo store: no real payment is taken.")
