"""Cart (S3). Public: guests can fill a cart. Owner: User 2.

Stories: US-CART-02 (U2-01), US-CART-03 (U2-07). Use utils.cart, services.cart_lines.load_cart_lines,
utils.pricing.calculate_totals, and build the totals box in components/cart_summary.py.
"""

import logging
from dataclasses import replace
from pathlib import Path

import streamlit as st

from components.cart_summary import cart_summary
from components.states import empty_state, error_state
from models.cart import CartLine
from services.cart_lines import load_cart_lines
from utils import cart
from utils.formatting import money
from utils.pricing import calculate_totals

logger = logging.getLogger(__name__)

_PLACEHOLDER = Path(__file__).resolve().parent.parent / "assets" / "images" / "product-placeholder.svg"


# ---------------------------------------------------------------- button callbacks
# Callbacks run BEFORE the page redraws, so the totals and the "Cart (N)" menu count are right
# on the same click.


def _qty_changed(sku: str, key: str) -> None:
    cart.update(sku, int(st.session_state[key]))


def _remove(sku: str, name: str) -> None:
    cart.remove(sku)
    st.toast(f"Removed {name} from your cart", icon=":material/delete:")


# ---------------------------------------------------------------- checks before showing the cart


def _drop_missing(lines: list[CartLine]) -> None:
    """Drives that no longer exist (or are hidden) are taken out, with a message (AC3)."""
    found = {line.sku for line in lines}
    missing = [sku for sku in cart.get_cart() if sku not in found]
    for sku in missing:
        cart.remove(sku)
    if missing:
        st.warning(f"{len(missing)} item(s) are no longer sold and were removed: {', '.join(missing)}.",
                   icon=":material/info:")


def _cap_to_stock(lines: list[CartLine]) -> list[CartLine]:
    """If stock went down since the drive was added, lower the quantity and say so (AC3)."""
    capped = []
    for line in lines:
        if line.available and line.qty > line.max_qty:
            cart.update(line.sku, line.max_qty, max_qty=line.max_qty)
            st.warning(f"Only {line.max_qty} of {line.name} can be ordered now, so your cart was updated.",
                       icon=":material/inventory:")
            line = replace(line, qty=line.max_qty)
        capped.append(line)
    return capped


# ---------------------------------------------------------------- drawing


def _image(line: CartLine) -> None:
    if line.image_url:
        st.image(line.image_url, alt=line.name, width=72)
    else:
        st.image(_PLACEHOLDER.read_text(encoding="utf-8"), alt=f"{line.name} (no photo yet)", width=72)


def _line(line: CartLine) -> None:
    """One cart row: image, name and price, quantity stepper, line total and remove (AC1)."""
    with st.container(border=True, key=f"cart_line_{line.sku}"):
        picture, about, qty, total, remove = st.columns([1, 4, 2, 2, 2],vertical_alignment="center")
        with picture:
            _image(line)
        with about:
            st.markdown(f"**{line.name}**")
            st.caption(f"{line.sku} · {money(line.unit_price_cents)} each")
        with qty:
            if line.available:
                key = f"cart_qty_{line.sku}"
                st.session_state[key] = line.qty  # always start from what the cart really holds
                st.number_input("Quantity", min_value=1, max_value=line.max_qty, step=1, key=key,
                                on_change=_qty_changed, args=(line.sku, key))
            else:  # sold out or hidden: flagged, and it blocks checkout (AC3)
                st.badge("Not available", color="red", icon=":material/block:")
        with total:
            st.markdown(f"**{money(line.line_total_cents)}**" if line.available else "—")
        with remove:
            # A visible word, not just a bin icon, so screen readers and everyone know what it does.
            st.button("Remove", icon=":material/delete:", help=f"Remove {line.name}",
                      key=f"remove_{line.sku}", on_click=_remove, args=(line.sku, line.name))


def _empty_cart() -> None:
    """AC4: an empty state, and Checkout can't be clicked."""
    empty_state("Your cart is empty.", icon=":material/shopping_cart:", action_label="Browse drives",
                action_page="app_pages/shop.py")
    st.page_link("app_pages/checkout.py", label="Proceed to checkout", disabled=True,
                 icon=":material/shopping_cart_checkout:")


def _show_cart() -> None:
    if not cart.get_cart():
        _empty_cart()
        return

    try:
        lines = load_cart_lines(dict(cart.get_cart()))
    except Exception:  # never show raw database errors to shoppers (NFR-SEC-08)
        logger.exception("cart: could not load prices")
        if error_state("We couldn't load your cart's prices right now.", key="cart_retry"):
            st.rerun()
        return

    _drop_missing(lines)
    lines = _cap_to_stock(lines)
    if not lines:
        _empty_cart()
        return

    items = sum(line.qty for line in lines if line.available)
    st.subheader(f"Your cart ({items} item{'s' if items != 1 else ''})")
    for line in lines:
        _line(line)

    blocked = [line.name for line in lines if not line.available]
    if blocked:
        st.error(f"Remove these before checking out, they can't be ordered right now: {', '.join(blocked)}.",
                 icon=":material/block:")

    # Totals only count what can actually be ordered. Prices are today's (AC2).
    cart_summary(calculate_totals([line for line in lines if line.available]))

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.page_link("app_pages/shop.py", label="Continue shopping", icon=":material/arrow_back:")
        st.page_link("app_pages/checkout.py", label="Proceed to checkout", disabled=bool(blocked),
                     icon=":material/shopping_cart_checkout:")


_show_cart()
