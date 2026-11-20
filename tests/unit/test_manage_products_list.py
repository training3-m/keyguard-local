"""U3-01 · US-MGT-02 Manage > Products list (services/admin_products.py, app_pages/manage_products.py)."""

import pytest
from streamlit.testing.v1 import AppTest

from services.admin_products import list_all_products
from tests.conftest import APP_FILE

# ---------------------------------------------------------------- service


def test_lists_every_product_including_hidden_sorted_by_sku(fake_client):
    skus = [p.sku for p in list_all_products()]
    assert skus == sorted(skus)
    assert "KG-ESS-8" in skus  # the hidden one


def test_can_leave_out_hidden_products(fake_client):
    assert "KG-ESS-8" not in [p.sku for p in list_all_products(include_inactive=False)]


def test_search_by_name_or_sku_ignores_case(fake_client):
    assert [p.sku for p in list_all_products("rancho")] == ["KG-RCE-32"]
    assert [p.sku for p in list_all_products("kg-ess")] == ["KG-ESS-16", "KG-ESS-8"]


# ---------------------------------------------------------------- page


def _open_manage_products() -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    at = AppTest.from_file(str(APP_FILE), default_timeout=30).run()
    return at.switch_page("app_pages/manage_products.py").run()


def test_staff_sees_all_products_with_hidden_count(fake_settings, fake_client, as_user):
    as_user("staff")
    at = _open_manage_products()
    assert not at.exception
    assert "6 products · 1 hidden from the shop" in [c.value for c in at.caption]
    assert len(at.dataframe[0].value) == 6


def test_search_narrows_the_table(fake_settings, fake_client, as_user):
    as_user("owner")
    at = _open_manage_products()
    at.text_input(key="manage_products_search").input("pro").run()
    assert list(at.dataframe[0].value["SKU"]) == ["KG-PRO-256", "KG-PRO-64"]


def test_customer_does_not_even_get_the_page(fake_settings, fake_client, as_user):
    # US-MGT-01 AC1: for customers the Manage pages are not registered at all, so there is nothing
    # to open. (If someone got past that, require_role and the database rules still stop them.)
    as_user("customer")
    with pytest.raises(ValueError, match="Could not find a navigation page"):
        _open_manage_products()
