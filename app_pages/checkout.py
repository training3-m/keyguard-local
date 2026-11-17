"""Checkout (S6) and, with ?order=..., the order confirmation (S7). Sign-in required. Owner: User 2.

Stories: US-CHK-01 gate (U2-02), US-CHK-02 form (U2-03), US-CHK-05 confirmation (U2-04),
US-CHK-04 email file (U2-05). Stock is lowered by the database function for US-CHK-03 (0007). No card or payment field may ever appear here (NFR-SEC-02).
"""

import streamlit as st

from components.states import coming_soon
from utils.guards import require_signed_in

user = require_signed_in("Sign in to check out. Your cart is saved.", return_to="app_pages/checkout.py")

order_number = st.query_params.get("order")
if order_number:
    coming_soon("US-CHK-05 · U2-04", f"the confirmation for order {order_number}")
else:
    coming_soon("US-CHK-02 · U2-03", "the demo checkout form (no payment needed)")
