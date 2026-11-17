"""KeyGuard Local: the app's entry point.

Run it with:  streamlit run streamlit_app.py

It checks the settings, works out who is signed in, builds the menu for that person, and runs the
chosen page. Foundation Prompt E adds every other page here; stories never edit this file (CLAUDE.md).
"""

import streamlit as st

from services.auth import current_user, sign_out
from utils.config import require_settings

st.set_page_config(page_title="KeyGuard Local", page_icon=":material/lock:", layout="wide")

require_settings()  # stops with a clear message if the Supabase settings are missing
user = current_user()

shop = st.Page("app_pages/shop.py", title="Shop", icon=":material/storefront:", default=True,
               help="Browse keypad-locked USB drives and accessories.")
sign_in_page = st.Page("app_pages/sign_in.py", title="Sign in", icon=":material/login:",
                       help="Sign in as a customer, staff member or the owner.")
register_page = st.Page("app_pages/register.py", title="Register", icon=":material/person_add:",
                        help="Create a free customer account so you can check out.")

# The menu only shows pages this person may use (NFR-ROLE-02, layer 1).
pages: dict[str, list] = {"": [shop]}
if user is None:
    pages["Account"] = [sign_in_page, register_page]
page = st.navigation(pages, position="sidebar")

with st.sidebar:
    if user:
        with st.container(border=True):
            st.markdown(f":material/account_circle: **{user.display_name}**")
            st.badge(user.role.upper(), color="violet" if user.is_staff_or_owner else "blue")
            if st.button("Sign out", icon=":material/logout:", width="stretch"):
                sign_out()
                st.rerun()

st.title(page.title)
page.run()

st.divider()
st.caption(":material/info: KeyGuard Local is a demo store for training: no real orders, payments or emails.")
