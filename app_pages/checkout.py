"""Checkout (S6) and, with ?order=..., the order confirmation (S7). Sign-in required. Owner: User 2.

Stories: US-CHK-01 gate (U2-02), US-CHK-02 form (U2-03), US-CHK-05 confirmation (U2-04),
US-CHK-04 email file (U2-05). Stock is lowered by the database function for US-CHK-03 (0007). No card or payment field may ever appear here (NFR-SEC-02).
"""

import logging
from uuid import UUID, uuid4

import streamlit as st

from components.cart_summary import cart_summary
from components.states import coming_soon, empty_state, error_state
from models.cart import CartLine
from models.user import UserProfile
from services.cart_lines import load_cart_lines
from services.orders import OrderError, place_order
from utils import cart
from utils.formatting import money
from utils.guards import require_signed_in
from utils.pricing import calculate_totals
from validation.checkout import checkout_errors

logger = logging.getLogger(__name__)

# Session State keys used by this page.
_KEY = "checkout_key"            # one random id per checkout attempt: a double click = one order
_PLACING = "checkout_placing"    # True while the order is being placed: the button is disabled
_ERRORS = "checkout_errors"      # {field: message} shown under each field
_ORDER_ERROR = "checkout_order_error"  # (message, out_of_stock) from the database
_FIELDS = ("full_name", "address", "city", "zip")


def _start_placing() -> None:
    """Runs on the Place order click, before the page redraws, so the button shows disabled (AC3)."""
    st.session_state[_PLACING] = True


def _field_error(field: str) -> None:
    """The message under a field, if the last try had a problem with it (AC3: errors inline)."""
    message = st.session_state.get(_ERRORS, {}).get(field)
    if message:
        st.error(message, icon=":material/error:")


def _order_summary(lines: list[CartLine]) -> None:
    """The right-hand column: each line, then the totals box (02-ui-ux.md §4.5)."""
    st.subheader("Order summary")
    for line in lines:
        with st.container(horizontal=True, horizontal_alignment="distribute"):
            st.markdown(f"{line.qty} × {line.name}")
            st.markdown(money(line.line_total_cents))
    cart_summary(calculate_totals(lines))


def _checkout_form(user: UserProfile) -> None:
    """The left-hand column: email (read-only), name, address, city, ZIP, demo box (US-CHK-02 AC1)."""
    st.info("Demo store: no payment is taken and nothing is shipped. Use made-up address details.",
            icon=":material/info:")
    st.text_input("Email", value=user.email, disabled=True,
                  help="The confirmation goes to your account email.")

    st.session_state.setdefault("checkout_full_name", user.full_name or "")  # prefilled, can be changed
    order_error = st.session_state.get(_ORDER_ERROR)
    if order_error:
        message, out_of_stock = order_error
        st.error(message, icon=":material/error:")
        if out_of_stock:  # US-CHK-03 AC2: back to the cart, which shows the new stock
            st.page_link("app_pages/cart.py", label="Review your cart", icon=":material/shopping_cart:")

    # AC2: there is NO card, CVV or payment field, here or anywhere else.
    with st.form("checkout_form", border=True):
        st.text_input("Full name", max_chars=80, autocomplete="name", key="checkout_full_name")
        _field_error("full_name")
        st.text_input("Address", max_chars=120, autocomplete="street-address", key="checkout_address")
        _field_error("address")
        city, zip_code = st.columns([2, 1])
        with city:
            st.text_input("City", max_chars=60, autocomplete="address-level2", key="checkout_city")
            _field_error("city")
        with zip_code:
            st.text_input("ZIP", max_chars=5, autocomplete="postal-code", placeholder="91730",
                          key="checkout_zip")
            _field_error("zip")
        st.checkbox("I understand this is a demo and no real order is placed", key="checkout_demo")
        _field_error("demo")
        st.form_submit_button("Place order", type="primary", icon=":material/check_circle:",
                              disabled=st.session_state.get(_PLACING, False), on_click=_start_placing)


def _place_order_now() -> None:
    """Checks the form, then asks the database to place the order. Runs once per click."""
    st.session_state.pop(_PLACING, None)
    st.session_state.pop(_ORDER_ERROR, None)
    shipping = {field: str(st.session_state.get(f"checkout_{field}", "")) for field in _FIELDS}
    errors = checkout_errors(shipping, bool(st.session_state.get("checkout_demo")))
    st.session_state[_ERRORS] = errors
    if errors:
        st.rerun()  # show the messages under the fields

    key = UUID(st.session_state.setdefault(_KEY, str(uuid4())))
    try:
        with st.spinner("Placing your order…"):
            result = place_order(dict(cart.get_cart()), shipping, key)
    except OrderError as error:
        # Nothing was saved, so the same key is safe to use for the next try.
        st.session_state[_ORDER_ERROR] = (error.message, error.out_of_stock)
        st.rerun()

    # Success: empty the cart, start a fresh key for the next checkout and show the confirmation.
    cart.clear()
    st.session_state.pop(_KEY, None)
    st.session_state.pop("checkout_demo", None)
    st.query_params["order"] = str(result["order_number"])
    st.rerun()


def _show_checkout(user: UserProfile) -> None:
    if not cart.get_cart():
        empty_state("Your cart is empty.", icon=":material/shopping_cart:", action_label="Browse drives",
                    action_page="app_pages/shop.py")
        return

    try:
        lines = load_cart_lines(dict(cart.get_cart()))
    except Exception:  # never show raw database errors (NFR-SEC-08)
        logger.exception("checkout: could not load prices")
        if error_state("We couldn't load your cart's prices right now.", key="checkout_retry"):
            st.rerun()
        return

    # Anything sold out, hidden, gone or over stock is fixed on the cart page first.
    cart_now = cart.get_cart()
    if len(lines) != len(cart_now) or any(not ln.available or ln.qty > ln.max_qty for ln in lines):
        st.warning("Some items in your cart changed since you added them. Please review your cart.",
                   icon=":material/inventory:")
        st.page_link("app_pages/cart.py", label="Review your cart", icon=":material/shopping_cart:")
        return

    form_column, summary_column = st.columns([3, 2], gap="large")
    with form_column:
        _checkout_form(user)
    with summary_column:
        _order_summary(lines)

    if st.session_state.get(_PLACING):
        _place_order_now()


user = require_signed_in("Sign in to check out. Your cart is saved.", return_to="app_pages/checkout.py")

order_number = st.query_params.get("order")
if order_number:
    st.success(f"Thank you! Your order {order_number} is placed.", icon=":material/check_circle:")
    coming_soon("US-CHK-05 · U2-04", "the full confirmation with your items and the email download")
    st.page_link("app_pages/shop.py", label="Back to shop", icon=":material/storefront:")
else:
    _show_checkout(user)
