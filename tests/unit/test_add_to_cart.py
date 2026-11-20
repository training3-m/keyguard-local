"""U1-04 · US-CART-01 Add to cart on the product detail view (components/product_detail.py)."""

import pytest
from streamlit.testing.v1 import AppTest

from services.products import _active_product_rows
from tests.conftest import APP_FILE


@pytest.fixture(autouse=True)
def _fresh_cache():
    _active_product_rows.clear()
    yield
    _active_product_rows.clear()


def _open_detail(sku: str) -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    at = AppTest.from_file(str(APP_FILE), default_timeout=30)
    at.query_params["sku"] = sku
    return at.run()


def _add_button(at: AppTest, sku: str):
    return at.button(key=f"add_{sku}")


def test_guest_adds_a_drive_and_sees_a_toast(fake_settings, fake_client, as_user):
    as_user(None)  # AC4: guests can add
    at = _open_detail("KG-PRO-64")
    at.selectbox(key="qty_KG-PRO-64").select(2)
    _add_button(at, "KG-PRO-64").click().run()

    assert not at.exception
    assert at.session_state["cart"] == {"KG-PRO-64": 2}
    assert at.toast[0].value == "Added 2 × KeyGuard Pro 64 GB to cart"
    assert "In your cart: 2" in [c.value for c in at.caption]


def test_quantity_picker_stops_at_stock(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_detail("KG-PRO-256")  # only 3 in stock in the sample data
    assert at.selectbox(key="qty_KG-PRO-256").options == ["1", "2", "3"]  # AC1


def test_quantity_picker_stops_at_10(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_detail("KG-ESS-16")  # 40 in stock
    assert at.selectbox(key="qty_KG-ESS-16").options[-1] == "10"


def test_adding_again_is_capped_and_the_shopper_is_told(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_detail("KG-PRO-256")
    at.selectbox(key="qty_KG-PRO-256").select(3)
    _add_button(at, "KG-PRO-256").click().run()
    _add_button(at, "KG-PRO-256").click().run()  # 3 + 3 would be over the stock of 3

    assert at.session_state["cart"] == {"KG-PRO-256": 3}  # AC2
    assert at.toast[0].value.startswith("Limit reached: you can order up to 3")


def test_out_of_stock_button_is_disabled(fake_settings, fake_client, as_user):
    for row in fake_client.tables["products"]:
        if row["sku"] == "KG-PRO-64":
            row["stock_qty"] = 0
    as_user(None)
    at = _open_detail("KG-PRO-64")
    button = _add_button(at, "KG-PRO-64")
    assert button.label == "Out of stock"  # AC3
    assert button.disabled
