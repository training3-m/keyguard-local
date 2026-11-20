"""U1-03 · US-PDP-01 product detail: get_product (services/products.py) and the ?sku= view."""

import pytest
from streamlit.testing.v1 import AppTest

from components.product_detail import spec_rows
from models.product import Product
from services.products import _active_product_rows, get_product
from tests.conftest import APP_FILE, SAMPLE_PRODUCTS


@pytest.fixture(autouse=True)
def _fresh_cache():
    _active_product_rows.clear()
    yield
    _active_product_rows.clear()


# ---------------------------------------------------------------- service


def test_get_product_finds_an_active_drive(fake_client):
    product = get_product("KG-PRO-256")
    assert product is not None
    assert product.name == "KeyGuard Pro 256 GB RGB Edition"


def test_get_product_ignores_case_and_spaces(fake_client):
    product = get_product("  kg-pro-64 ")
    assert product is not None and product.sku == "KG-PRO-64"


@pytest.mark.parametrize("sku", ["KG-ESS-8", "KG-NOPE-1", ""])
def test_hidden_or_unknown_sku_returns_none(fake_client, sku):
    assert get_product(sku) is None  # AC2: KG-ESS-8 is inactive


def test_spec_rows_put_capacity_and_color_first():
    pro_256 = Product.from_row(next(r for r in SAMPLE_PRODUCTS if r["sku"] == "KG-PRO-256"))
    assert spec_rows(pro_256) == [
        {"Spec": "Capacity", "Value": "256 GB"},
        {"Spec": "Color", "Value": "Midnight Black with RGB keypad glow"},
        {"Spec": "Lighting", "Value": "RGB keypad glow (slow fade, no flashing)"},
    ]


# ---------------------------------------------------------------- page


def _open_detail(sku: str) -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    at = AppTest.from_file(str(APP_FILE), default_timeout=30)
    at.query_params["sku"] = sku
    return at.run()


def test_detail_page_shows_everything_ac1_asks_for(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_detail("KG-PRO-256")
    assert not at.exception
    assert at.header[0].value == "KeyGuard Pro 256 GB RGB Edition"
    assert "SKU KG-PRO-256 · Pro" in [c.value for c in at.caption]
    text = " ".join(m.value for m in at.markdown)
    assert "$139.00" in text
    assert "Security HUD" in text
    assert [t.label for t in at.tabs] == ["Overview", "Specs", "How the keypad works", "Community"]
    assert "1. Type your PIN" in text
    assert "Rancho Public Library Digital Safety Fund" in text


def test_unknown_sku_shows_product_not_found(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_detail("KG-NOPE-1")
    assert not at.exception
    assert at.warning[0].value == "Product not found."  # AC2


def test_hidden_sku_shows_product_not_found_even_for_staff(fake_settings, fake_client, as_user):
    as_user("staff")  # staff may read hidden rows in the database, but the shop must not show them
    at = _open_detail("KG-ESS-8")
    assert at.warning[0].value == "Product not found."


def test_detail_database_error_is_friendly(fake_settings, fake_client, as_user, monkeypatch):
    def broken_table(_name):
        raise RuntimeError("database down")

    monkeypatch.setattr(fake_client, "table", broken_table)
    as_user(None)
    at = _open_detail("KG-PRO-64")
    assert not at.exception
    assert at.error[0].value == "We couldn't load this drive right now."
