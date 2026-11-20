"""Manage > Products (S11, S12). Staff and owner. Owner: User 3.

Stories: US-MGT-02 list (U3-01), US-MGT-05 hide/show (U3-02), US-MGT-03 create (U3-03),
US-MGT-04 bulk edit (U3-04), US-MGT-07 image (U3-05), US-MGT-06 delete (U3-06).
Use services.admin_products and services.storage; the add/edit form goes in components/product_form.py.
Staff never see price, gift, Add or Delete controls (02-ui-ux.md §4.10).
"""

import logging

import streamlit as st

from components.states import error_state
from models.product import LOW_STOCK_THRESHOLD, Product
from services.admin_products import list_all_products
from utils.guards import require_role

logger = logging.getLogger(__name__)

user = require_role("staff", "owner")  # page guard; the database rules are the real lock (0005)


def _table_rows(products: list[Product]) -> list[dict]:
    """One row per product for the table. Money is shown in dollars."""
    return [
        {
            "SKU": p.sku,
            "Name": p.name,
            "Category": p.category,
            "Price": p.price_cents / 100,
            "Gift": p.community_gift_cents / 100,
            "Stock": p.stock_qty,
            "Low": "Low" if p.is_active and p.stock_qty <= LOW_STOCK_THRESHOLD else "",
            "Active": p.is_active,
        }
        for p in products
    ]


def _show_products() -> None:
    with st.container(horizontal=True, vertical_alignment="bottom"):
        term = st.text_input("Search by name or SKU", placeholder="KG-PRO or Rancho", max_chars=60,
                             icon=":material/search:", live=True, key="manage_products_search")
        show_inactive = st.checkbox("Show inactive", value=True, key="manage_products_inactive")

    try:
        products = list_all_products(term, include_inactive=show_inactive)
    except Exception:  # never show raw database errors (NFR-SEC-08)
        logger.exception("manage products: could not load")
        if error_state("We couldn't load the products right now.", key="manage_products_retry"):
            st.rerun()
        return

    if not products:
        st.info(f"No products match '{term.strip()}'." if term.strip() else "No products yet.",
                icon=":material/search_off:")
        return

    hidden = sum(1 for p in products if not p.is_active)
    st.caption(f"{len(products)} product{'s' if len(products) != 1 else ''}"
               + (f" · {hidden} hidden from the shop" if hidden else ""))
    st.dataframe(
        _table_rows(products),
        hide_index=True,
        width="stretch",
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Gift": st.column_config.NumberColumn("To Rancho", format="$%.2f"),
            "Low": st.column_config.TextColumn("Low stock", help=f"{LOW_STOCK_THRESHOLD} or fewer left"),
            "Active": st.column_config.CheckboxColumn("In shop", help="Unticked = hidden from shoppers"),
        },
    )


_show_products()
