"""The product detail view, shown on the Shop page as ?sku=... (02-ui-ux.md §4.3). Owner: User 1.

Stories: US-PDP-01 (U1-03) builds this view; US-CART-01 (U1-04) adds quantity and Add to cart;
US-PDP-02 (U1-08) adds "You may also like".
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from components.badges import community_chip, stock_badge
from components.security_hud import lock_indicator, security_hud
from models.product import Product
from utils import cart
from utils.formatting import money

_TOAST_KEY = "_cart_toast"  # the message to show after an Add to cart click
_PLACEHOLDER = Path(__file__).resolve().parent.parent / "assets" / "images" / "product-placeholder.svg"

# Friendly names for the keys in products.specs (seed data, 01_products.sql).
_SPEC_LABELS = {
    "encryption": "Encryption",
    "pin_length": "PIN length",
    "auto_wipe": "Auto-wipe",
    "read_only_mode": "Read-only mode",
    "lighting": "Lighting",
    "connector": "Connector",
    "warranty": "Warranty",
    "contents": "In the box",
}


def _image(product: Product) -> None:
    if product.image_url:
        st.image(product.image_url, alt=product.name, width="stretch")
    else:
        st.image(_PLACEHOLDER.read_text(encoding="utf-8"), alt=f"{product.name} (no photo yet)",
                 width="stretch")


def _summary(product: Product) -> None:
    """Name, SKU, price, stock and gift: the right-hand column at the top."""
    st.header(product.name)
    st.caption(f"SKU {product.sku} · {product.category}")
    st.markdown(f"## {money(product.price_cents)}")
    with st.container(horizontal=True, gap="small"):
        stock_badge(product.stock_qty, is_active=product.is_active)
        community_chip(product.community_gift_cents)
    _add_to_cart(product)
    st.page_link("app_pages/shop.py", label="Back to shop", icon=":material/arrow_back:")


def _on_add(product: Product, qty_key: str) -> None:
    """Runs when Add to cart is clicked, BEFORE the page redraws, so the "Cart (N)" count in the
    menu already includes the new items on this same click (US-CART-01 AC1)."""
    qty = int(st.session_state[qty_key])
    before = cart.get_cart().get(product.sku, 0)
    after = cart.add(product.sku, qty, max_qty=product.max_order_qty)
    if after < before + qty:  # AC2: tell the shopper when the limit stopped the add
        message = (f"Limit reached: you can order up to {product.max_order_qty} of {product.name}. "
                   f"Your cart has {after}.")
        st.session_state[_TOAST_KEY] = (message, ":material/info:")
    else:
        st.session_state[_TOAST_KEY] = (f"Added {qty} × {product.name} to cart",
                                        ":material/add_shopping_cart:")


def _add_to_cart(product: Product) -> None:
    """Quantity picker and Add to cart (US-CART-01). Guests can add too (AC4)."""
    if not product.in_stock:  # AC3
        st.button("Out of stock", disabled=True, icon=":material/remove_shopping_cart:",
                  key=f"add_{product.sku}")
        return

    qty_key = f"qty_{product.sku}"
    with st.container(horizontal=True, vertical_alignment="bottom"):
        # AC1: 1 up to 10, or fewer when stock is lower.
        st.selectbox("Qty", options=list(range(1, product.max_order_qty + 1)), key=qty_key, width=90)
        st.button("Add to cart", type="primary", icon=":material/add_shopping_cart:",
                  key=f"add_{product.sku}", on_click=_on_add, args=(product, qty_key))

    in_cart = cart.get_cart().get(product.sku, 0)
    if in_cart:
        st.caption(f"In your cart: {in_cart}")
    toast = st.session_state.pop(_TOAST_KEY, None)
    if toast:
        st.toast(toast[0], icon=toast[1])


def spec_rows(product: Product) -> list[dict[str, str]]:
    """The Specs table as rows of {"Spec", "Value"}: capacity and color first, then the specs field."""
    rows = []
    if product.capacity_gb:
        rows.append({"Spec": "Capacity", "Value": f"{product.capacity_gb} GB"})
    if product.color:
        rows.append({"Spec": "Color", "Value": product.color})
    for key, value in product.specs.items():
        label = _SPEC_LABELS.get(key, key.replace("_", " ").capitalize())
        rows.append({"Spec": label, "Value": str(value)})
    return rows


def _keypad_steps() -> None:
    """Three steps, with the lock light going from red to green. No animation: still images only."""
    steps = [
        (":material/dialpad:", "1. Type your PIN", "Press your 7-15 digit PIN on the drive's keypad.", True),
        (":material/lock_open:", "2. The light turns green", "Right PIN: the LED changes from red to green.",
         False),
        (":material/usb:", "3. Plug it in", "The drive now shows up on any computer, no software needed.",
         False),
    ]
    for column, (icon, title, text, locked) in zip(st.columns(3), steps):
        with column, st.container(border=True, height="stretch"):
            st.markdown(f"**{icon} {title}**")
            st.write(text)
            lock_indicator(locked)
    st.caption("Unplug it, or leave it idle, and it locks itself again. "
               "After 10 wrong PINs it wipes itself so nobody can keep guessing.")


def _community(product: Product) -> None:
    if product.community_gift_cents > 0:
        st.markdown(f"**{money(product.community_gift_cents)}** from every one sold goes to the "
                    "Rancho Public Library Digital Safety Fund.")
    st.write("The fund runs free classes in Rancho on password safety and data privacy. "
             "The running total is shown in the banner at the top of every page.")
    st.caption("Rancho and its library fund are fictional, part of this demo store.")


def product_detail(product: Product) -> None:
    """The whole detail view for one active product (US-PDP-01 AC1)."""
    left, right = st.columns([1, 1], gap="large")
    with left:
        _image(product)
    with right:
        _summary(product)

    security_hud(product)

    overview, specs, keypad, community = st.tabs(
        ["Overview", "Specs", "How the keypad works", "Community"])
    with overview:
        st.write(product.description or "No description yet.")
    with specs:
        rows = spec_rows(product)
        if rows:
            st.dataframe(rows, hide_index=True, width="stretch")
        else:
            st.write("No specs listed for this product.")
        st.caption("Fictional product: demo copy, not certified security claims.")
    with keypad:
        _keypad_steps()
    with community:
        _community(product)
