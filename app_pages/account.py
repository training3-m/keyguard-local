"""My Account (S8, S9). Sign-in required. Owner: Tech Lead (layout only).

This page only places the two tabs; the tabs belong to their stories, so nobody else edits this file:
- Profile   -> components/account_profile.py (User 1, US-AUTH-04, U1-07)
- My orders -> components/my_orders.py       (User 2, US-CHK-06, U2-08)
"""

import streamlit as st

from components.account_profile import render_account_profile
from components.my_orders import render_my_orders
from utils.guards import require_signed_in

user = require_signed_in("Sign in to see your account.", return_to="app_pages/account.py")

profile_tab, orders_tab = st.tabs([":material/person: Profile", ":material/receipt_long: My orders"])
with profile_tab:
    render_account_profile(user)
with orders_tab:
    render_my_orders(user)
