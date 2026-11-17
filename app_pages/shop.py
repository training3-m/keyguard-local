"""Shop: the catalog (S1) and, with ?sku=..., the product detail view (S2). Public. Owner: User 1.

Stories: US-SRCH-01 (U1-01), US-SRCH-02 (U1-02), US-SRCH-03 (U1-06), US-SRCH-04 (U1-09, filters kept in
the URL with widget bind="query-params"), US-PDP-01 (U1-03), US-PDP-02 (U1-08), US-CART-01 (U1-04).
Build the detail view in components/product_detail.py and the filters in components/filters.py.
"""

import streamlit as st

from components.states import coming_soon

sku = st.query_params.get("sku")

if sku:
    coming_soon("US-PDP-01 · U1-03", f"details, Security HUD and Add to cart for {sku}")
    st.page_link("app_pages/shop.py", label="Back to shop", icon=":material/arrow_back:")
else:
    coming_soon("US-SRCH-01 · U1-01", "search and browse the KeyGuard catalog")
