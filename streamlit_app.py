"""KeyGuard Local: the app's entry point and menu (foundation FND-11, 02-ui-ux.md §3 site map).

Run it with:  streamlit run streamlit_app.py --server.headless=true

It loads the theme, checks the settings, works out who is signed in, builds the menu for that person,
and runs the chosen page. EVERY page is registered here already, so stories never edit this file
(CLAUDE.md). Need a new page? Ask the Tech Lead.
"""

import streamlit as st

from components.app_header import app_header, load_theme_css
from components.badges import role_badge
from services.auth import current_user, sign_out
from utils import cart
from utils.config import require_settings

st.set_page_config(page_title="KeyGuard Local", page_icon=":material/lock:", layout="wide")
load_theme_css()
require_settings()  # stops with a clear message if the Supabase settings are missing
user = current_user()

# --- Every page in the site map (02-ui-ux.md §3) -------------------------------------------------
cart_items = cart.count()
shop = st.Page("app_pages/shop.py", title="Shop", icon=":material/storefront:", default=True,
               help="Browse keypad-locked USB drives and accessories, and open a drive's details.")
cart_page = st.Page("app_pages/cart.py", title=f"Cart ({cart_items})" if cart_items else "Cart",
                    icon=":material/shopping_cart:", url_path="cart",
                    help="See and change what you're buying. Guests can fill a cart too.")
checkout = st.Page("app_pages/checkout.py", title="Checkout", icon=":material/shopping_cart_checkout:",
                   help="Place a demo order. Sign-in required; no payment needed.")
sign_in_page = st.Page("app_pages/sign_in.py", title="Sign in", icon=":material/login:",
                       help="Sign in as a customer, staff member or the owner.")
register_page = st.Page("app_pages/register.py", title="Register", icon=":material/person_add:",
                        help="Create a free customer account so you can check out.")
account = st.Page("app_pages/account.py", title="My account", icon=":material/account_circle:",
                  help="Your profile and your past orders.")
dashboard = st.Page("app_pages/manage_dashboard.py", title="Dashboard", icon=":material/monitoring:",
                    help="Store overview: orders, units sold, low stock and recent orders.")
manage_products = st.Page("app_pages/manage_products.py", title="Products", icon=":material/inventory_2:",
                          help="Edit stock, details and images; hide or show products.")
manage_orders = st.Page("app_pages/manage_orders.py", title="Orders", icon=":material/receipt_long:",
                        help="See every order and move it to Packed or Shipped.")
manage_users = st.Page("app_pages/manage_users.py", title="Staff & users", icon=":material/group:",
                       help="Owner only: make a customer staff, or back.")

# --- The menu only shows pages this person may use (US-MGT-01, NFR-ROLE-02 layer 1) --------------
pages: dict[str, list] = {"": [shop, cart_page, checkout]}
if user is None:
    pages["Account"] = [sign_in_page, register_page]
else:
    pages["Account"] = [account]
    if user.is_staff_or_owner:
        pages["Manage"] = [dashboard, manage_products, manage_orders]
        if user.is_owner:
            pages["Manage"].append(manage_users)
page = st.navigation(pages, position="sidebar")

# After signing in or registering, the sign-in page asks to go somewhere that only exists in the
# menu for a signed-in user (for example the Dashboard); switch now that the menu includes it.
redirect = st.session_state.pop("redirect_to", None)
if redirect:
    st.switch_page(redirect)

# --- Sidebar: who is signed in ---------------------------------------------------------------------
with st.sidebar:
    if user:
        with st.container(border=True):
            st.markdown(f":material/account_circle: **{user.display_name}**")
            role_badge(user.role)
            # Sign out keeps the cart (US-AUTH-03).
            if st.button("Sign out", icon=":material/logout:", width="stretch", key="sign_out"):
                sign_out()
                st.rerun()

# --- Page ------------------------------------------------------------------------------------------
app_header()
st.title(page.title)
page.run()

st.divider()
st.caption(":material/info: KeyGuard Local is a demo store for training: no real orders, payments or emails.")
