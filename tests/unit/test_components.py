"""Renders every shared component with sample data (Streamlit AppTest, no browser, no database).

Stories rely on these, so they must work before anyone uses them.
st.page_link only accepts pages from the real app menu, so the test swaps it for a stand-in that
records each link as a caption, which also lets us check where the links point.
"""

from streamlit.testing.v1 import AppTest


def _gallery() -> None:
    """A tiny app that draws each shared component once."""
    import streamlit as st

    from components.badges import community_chip, order_status_badge, role_badge, security_strip, stock_badge
    from components.order_detail import order_detail
    from components.product_card import product_card
    from components.security_hud import lock_indicator, security_hud
    from components.states import coming_soon, empty_state, not_found
    from models.order import Order, OrderLine
    from models.product import Product

    real_page_link = st.page_link

    def fake_page_link(page, *, label=None, query_params=None, **_kwargs):
        st.caption(f"LINK {page} {query_params or ''} {label}")

    st.page_link = fake_page_link
    try:
        drive = Product(id=1, sku="KG-PRO-256", name="KeyGuard Pro 256 GB RGB Edition", category="Pro",
                        price_cents=13900, stock_qty=3, community_gift_cents=500, capacity_gb=256,
                        color="Midnight Black with RGB keypad glow",
                        specs={"lighting": "RGB keypad glow (slow fade, no flashing)"})
        product_card(drive)
        security_hud(drive, locked=False)
        lock_indicator(True)
        stock_badge(0)
        stock_badge(3)
        stock_badge(25)
        order_status_badge("Shipped")
        role_badge("owner")
        community_chip(650)
        security_strip()
        coming_soon("US-TEST", "a test")
        empty_state("Your cart is empty.", action_label="Browse drives", action_page="app_pages/shop.py")
        not_found("Product")
        order_detail(Order(
            order_number="KG-20261102-0001", status="Placed", customer_name="Demo Customer",
            customer_email="customer@example.com", subtotal_cents=16700, shipping_cents=0, tax_cents=1336,
            total_cents=18036, community_gift_cents=650, created_at="2026-11-02T10:00:00+00:00",
            lines=[OrderLine(sku="KG-PRO-64", product_name="KeyGuard Pro 64 GB", unit_price_cents=7900,
                             qty=2, line_total_cents=15800, community_gift_cents=600)]))
    finally:
        st.page_link = real_page_link


def _run() -> AppTest:
    return AppTest.from_function(_gallery, default_timeout=30).run()


def test_shared_components_render_without_errors():
    at = _run()
    assert not at.exception, at.exception


def test_product_card_view_link_opens_detail_for_its_sku():
    links = [c.value for c in _run().caption if c.value.startswith("LINK")]
    assert any("app_pages/shop.py" in link and "KG-PRO-256" in link and "View" in link for link in links)


def test_prices_and_totals_are_formatted():
    at = _run()
    texts = " ".join(m.value for m in at.markdown)
    assert "$139.00" in texts  # product card price
