"""The product card used in the catalog grid and "You may also like" (02-ui-ux.md §2.3, UX-03)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from components.badges import community_chip, security_strip, stock_badge
from models.product import Product
from utils.formatting import money

_PLACEHOLDER = (Path(__file__).resolve().parent.parent / "assets" / "images" / "product-placeholder.svg")


def _image(product: Product) -> None:
    if product.image_url:
        st.image(product.image_url, alt=product.name, width="stretch")
    else:
        st.image(_PLACEHOLDER.read_text(encoding="utf-8"), alt=f"{product.name} (no photo yet)",
                 width="stretch")


def product_card(product: Product) -> None:
    """One bordered card: image, name, details, price, stock, security strip, gift and a View link.

    The View link opens the same Shop page with ?sku=..., where the detail view is shown (US-PDP-01).
    """
    with st.container(border=True, key=f"product_card_{product.sku}", height="stretch"):
        _image(product)
        st.markdown(f"**{product.name}**")
        details = " · ".join(str(part) for part in (
            f"{product.capacity_gb} GB" if product.capacity_gb else None, product.color) if part)
        if details:
            st.caption(details)
        st.markdown(f"### {money(product.price_cents)}")
        stock_badge(product.stock_qty, is_active=product.is_active)
        security_strip()
        community_chip(product.community_gift_cents)
        st.page_link("app_pages/shop.py", label="View", icon=":material/visibility:",
                     query_params={"sku": product.sku}, width="stretch")
