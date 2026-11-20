"""Shop: the catalog (S1) and, with ?sku=..., the product detail view (S2). Public. Owner: User 1.

Stories: US-SRCH-01 (U1-01), US-SRCH-02 (U1-02), US-SRCH-03 (U1-06), US-SRCH-04 (U1-09, filters kept in
the URL with widget bind="query-params"), US-PDP-01 (U1-03), US-PDP-02 (U1-08), US-CART-01 (U1-04).
Build the detail view in components/product_detail.py and the filters in components/filters.py.
"""

import logging

import streamlit as st

from components.product_card import product_card
from components.security_hud import security_hud
from components.states import coming_soon, error_state
from services.products import search_products

logger = logging.getLogger(__name__)

_SEARCH_KEY = "shop_search"
_COLUMNS = 3  # 3 cards per row on desktop; Streamlit stacks them on phones (02-ui-ux.md §4.2)


def _clear_search() -> None:
    """Runs before the page redraws, so the search box can still be emptied (US-SRCH-01 AC3)."""
    st.session_state[_SEARCH_KEY] = ""


def _plain(text: str) -> str:
    """Stops a search word like *abc* or `x` from being shown as bold or code."""
    return "".join(f"\\{ch}" if ch in "\\`*_{}[]()#+-.!|~<>$:" else ch for ch in text)


def _show_catalog() -> None:
    security_hud()

    # live=True: results update as the shopper types, no Enter needed (02-ui-ux.md §4.2).
    term = st.text_input(
        "Search drives",
        placeholder="Search drives (name, SKU, capacity)…",
        max_chars=60,
        icon=":material/search:",
        live=True,
        key=_SEARCH_KEY,
    )

    try:
        products = search_products(term)
    except Exception:  # never show raw database errors to shoppers (NFR-SEC-08)
        logger.exception("shop: could not load products")
        if error_state("We couldn't load the drives right now.", key="shop_retry"):
            st.rerun()
        return

    if not products:
        st.info(f"No drives match '{_plain(term.strip())}'", icon=":material/search_off:")
        st.button("Clear filters", icon=":material/filter_alt_off:", on_click=_clear_search)
        return

    st.caption(f"{len(products)} result{'s' if len(products) != 1 else ''}")
    for start in range(0, len(products), _COLUMNS):
        row = st.columns(_COLUMNS)
        for column, product in zip(row, products[start:start + _COLUMNS]):
            with column:
                product_card(product)


sku = st.query_params.get("sku")

if sku:
    coming_soon("US-PDP-01 · U1-03", f"details, Security HUD and Add to cart for {sku}")
    st.page_link("app_pages/shop.py", label="Back to shop", icon=":material/arrow_back:")
else:
    _show_catalog()
