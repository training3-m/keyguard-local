"""U2-01 · US-CART-02 cart page: load_cart_lines (services/cart_lines.py) and app_pages/cart.py."""

from streamlit.testing.v1 import AppTest

from services.cart_lines import load_cart_lines
from tests.conftest import APP_FILE

# ---------------------------------------------------------------- service


def test_lines_use_todays_database_price(fake_client):
    lines = load_cart_lines({"KG-PRO-64": 2, "KG-ACC-LAN": 1})
    assert [(line.sku, line.unit_price_cents, line.qty) for line in lines] == [
        ("KG-PRO-64", 7900, 2),
        ("KG-ACC-LAN", 900, 1),
    ]


def test_products_that_no_longer_exist_are_left_out(fake_client):
    assert [line.sku for line in load_cart_lines({"KG-GONE-1": 1, "KG-PRO-64": 1})] == ["KG-PRO-64"]


def test_empty_cart_does_not_ask_the_database(fake_client):
    assert load_cart_lines({}) == []
    assert fake_client.calls == []


# ---------------------------------------------------------------- page


def _open_cart(items: dict[str, int]) -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    at = AppTest.from_file(str(APP_FILE), default_timeout=30)
    at.session_state["cart"] = dict(items)
    at.run()
    return at.switch_page("app_pages/cart.py").run()


def _text(at: AppTest) -> str:
    return " ".join(str(m.value) for m in at.markdown)


def test_cart_shows_lines_and_totals(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_cart({"KG-PRO-64": 2, "KG-ACC-LAN": 1})  # 2 x $79 + $9 = $167
    assert not at.exception
    assert at.subheader[0].value == "Your cart (3 items)"
    text = _text(at)
    assert "$167.00" in text   # subtotal
    assert "FREE" in text      # over $75
    assert "$13.36" in text    # 8% tax
    assert "$180.36" in text   # total
    assert "$6.50" in text     # 2 x $3 + $0.50 to Rancho


def test_changing_quantity_updates_cart_and_totals(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_cart({"KG-ACC-LAN": 1})
    at.number_input(key="cart_qty_KG-ACC-LAN").set_value(3).run()
    assert at.session_state["cart"] == {"KG-ACC-LAN": 3}
    assert "$27.00" in _text(at)  # line total and subtotal


def test_remove_takes_the_line_out(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_cart({"KG-PRO-64": 1, "KG-ACC-LAN": 1})
    at.button(key="remove_KG-ACC-LAN").click().run()
    assert at.session_state["cart"] == {"KG-PRO-64": 1}
    assert at.toast[0].value == "Removed KeyGuard Lanyard & Cap Set from your cart"


def test_quantity_over_stock_is_capped_with_a_warning(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_cart({"KG-PRO-256": 8})  # only 3 in stock
    assert at.session_state["cart"] == {"KG-PRO-256": 3}
    assert "Only 3 of KeyGuard Pro 256 GB RGB Edition" in at.warning[0].value


def test_sold_out_line_is_flagged_and_blocks_checkout(fake_settings, fake_client, as_user):
    for row in fake_client.tables["products"]:
        if row["sku"] == "KG-PRO-64":
            row["stock_qty"] = 0
    as_user(None)
    at = _open_cart({"KG-PRO-64": 1, "KG-ACC-LAN": 1})
    assert "can't be ordered right now: KeyGuard Pro 64 GB" in at.error[0].value
    checkout_link = [p for p in at.get("page_link") if p.proto.label == "Proceed to checkout"][0]
    assert checkout_link.proto.disabled


def test_missing_product_is_removed_with_a_message(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_cart({"KG-GONE-1": 1, "KG-ACC-LAN": 1})
    assert at.session_state["cart"] == {"KG-ACC-LAN": 1}
    assert "no longer sold" in at.warning[0].value


def test_empty_cart_shows_empty_state_and_disabled_checkout(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_cart({})
    assert "Your cart is empty." in _text(at)
    checkout_link = [p for p in at.get("page_link") if p.proto.label == "Proceed to checkout"][0]
    assert checkout_link.proto.disabled
