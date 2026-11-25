"""U3-02 · US-MGT-05 hide / show a product (services/admin_products.set_active, Manage > Products)."""

import pytest
from postgrest.exceptions import APIError
from streamlit.testing.v1 import AppTest

from services.admin_products import ProductError, set_active
from tests.conftest import APP_FILE

# ---------------------------------------------------------------- service


def test_hiding_sends_one_update_for_that_sku(fake_client):
    set_active(" kg-pro-64 ", False)
    assert fake_client.calls == [("products", "update", {"is_active": False})]


def test_showing_sends_active_true(fake_client):
    set_active("KG-ESS-8", True)
    assert fake_client.calls == [("products", "update", {"is_active": True})]


def test_unknown_or_not_allowed_sku_is_reported_not_ignored(fake_client):
    # 0 rows back = the SKU doesn't exist, or the security rules skipped it (for example a customer).
    with pytest.raises(ProductError, match="KG-NOPE was not changed"):
        set_active("KG-NOPE", False)


def test_database_error_becomes_a_friendly_message(fake_client, monkeypatch):
    def broken(*_args, **_kwargs):
        raise APIError({"message": "permission denied for table products", "code": "42501"})

    monkeypatch.setattr(type(fake_client.table("products")), "execute", broken)
    with pytest.raises(ProductError) as error:
        set_active("KG-PRO-64", False)
    assert "permission denied" not in error.value.message  # never show raw database text


# ---------------------------------------------------------------- page


def _product_writes(fake_client) -> list:
    """Only the product changes (the header also asks for the community total, which is not a write)."""
    return [c for c in fake_client.calls if c[0] == "products"]


def _open(role: str, as_user) -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    as_user(role)
    at = AppTest.from_file(str(APP_FILE), default_timeout=30).run()
    return at.switch_page("app_pages/manage_products.py").run()


def test_hide_asks_first_then_saves(fake_settings, fake_client, as_user):
    at = _open("staff", as_user)
    at.selectbox(key="manage_active_sku").select("KG-PRO-64").run()
    at.button(key="manage_hide").click().run()
    assert _product_writes(fake_client) == []  # nothing saved yet: it asks first
    assert "KeyGuard Pro 64 GB" in at.warning[0].value

    at.button(key="manage_hide_yes").click().run()
    assert not at.exception
    assert _product_writes(fake_client) == [("products", "update", {"is_active": False})]
    assert "KeyGuard Pro 64 GB is now hidden from the shop." in [t.value for t in at.toast]


def test_cancel_saves_nothing(fake_settings, fake_client, as_user):
    at = _open("owner", as_user)
    at.selectbox(key="manage_active_sku").select("KG-PRO-64").run()
    at.button(key="manage_hide").click().run()
    at.button(key="manage_hide_cancel").click().run()
    assert _product_writes(fake_client) == []
    assert not at.warning


def test_hidden_product_can_be_shown_again_without_a_confirm(fake_settings, fake_client, as_user):
    at = _open("owner", as_user)
    at.selectbox(key="manage_active_sku").select("KG-ESS-8").run()
    at.button(key="manage_show").click().run()
    assert _product_writes(fake_client) == [("products", "update", {"is_active": True})]
    assert any("back in the shop" in t.value for t in at.toast)


def test_refusal_is_shown_as_an_error(fake_settings, fake_client, as_user, monkeypatch):
    import services.admin_products as admin_products

    def refused(_sku, _active):
        raise ProductError("Product KG-PRO-64 was not changed.")

    monkeypatch.setattr(admin_products, "set_active", refused)
    at = _open("staff", as_user)
    at.selectbox(key="manage_active_sku").select("KG-PRO-64").run()
    at.button(key="manage_hide").click().run()
    at.button(key="manage_hide_yes").click().run()
    assert "Product KG-PRO-64 was not changed." in [e.value for e in at.error]
