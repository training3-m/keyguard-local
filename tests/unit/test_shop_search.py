"""U1-01 · US-SRCH-01 keyword search: the service (services/products.py) and the Shop page."""

import pytest
from streamlit.testing.v1 import AppTest

from services.products import _active_product_rows, search_products
from tests.conftest import APP_FILE


@pytest.fixture(autouse=True)
def _fresh_cache():
    """The product list is cached for 30 seconds; each test starts with an empty cache."""
    _active_product_rows.clear()
    yield
    _active_product_rows.clear()


def _skus(products) -> list[str]:
    return [p.sku for p in products]


# ---------------------------------------------------------------- service


def test_empty_search_lists_active_drives_best_featured_first(fake_client):
    assert _skus(search_products()) == ["KG-PRO-64", "KG-RCE-32", "KG-PRO-256", "KG-ESS-16", "KG-ACC-LAN"]


def test_hidden_products_are_never_listed(fake_client):
    # AC2: KG-ESS-8 is inactive, even when searched for by its exact SKU.
    assert "KG-ESS-8" not in _skus(search_products())
    assert search_products("KG-ESS-8") == []


@pytest.mark.parametrize(
    ("term", "expected"),
    [
        ("rgb", ["KG-PRO-256"]),                      # name, lower case
        ("kg-acc", ["KG-ACC-LAN"]),                   # part of a SKU
        ("COMMUNITY", ["KG-RCE-32"]),                 # category, upper case
        ("client files", ["KG-PRO-64"]),              # description
        ("  rancho  ", ["KG-RCE-32"]),                # spaces around the word are ignored
    ],
)
def test_search_matches_name_sku_category_description(fake_client, term, expected):
    assert _skus(search_products(term)) == expected  # AC1


def test_no_match_returns_an_empty_list(fake_client):
    assert search_products("floppy disk") == []


def test_filters_are_not_built_yet(fake_client):
    with pytest.raises(NotImplementedError):
        search_products(category="Pro")  # U1-02 adds this


# ---------------------------------------------------------------- page


def _open_shop() -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    return AppTest.from_file(str(APP_FILE), default_timeout=30).run()


def test_shop_shows_a_card_for_each_active_drive(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_shop()
    assert not at.exception
    assert "5 results" in [c.value for c in at.caption]
    names = " ".join(m.value for m in at.markdown)
    assert "KeyGuard Pro 256 GB RGB Edition" in names
    assert "KeyGuard Essentials 8 GB" not in names  # inactive


def test_typing_a_search_narrows_the_grid(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_shop()
    at.text_input(key="shop_search").input("rancho").run()
    assert "1 result" in [c.value for c in at.caption]


def test_no_results_message_and_clear_button(fake_settings, fake_client, as_user):
    as_user(None)
    at = _open_shop()
    at.text_input(key="shop_search").input("xyz").run()
    assert at.info[0].value == "No drives match 'xyz'"  # AC3

    at.button[0].click().run()  # Clear filters
    assert at.text_input(key="shop_search").value == ""
    assert "5 results" in [c.value for c in at.caption]


def test_database_error_shows_a_friendly_message(fake_settings, fake_client, as_user, monkeypatch):
    def broken_table(_name):
        raise RuntimeError("database down")

    monkeypatch.setattr(fake_client, "table", broken_table)
    as_user(None)
    at = _open_shop()
    assert not at.exception
    assert at.error[0].value == "We couldn't load the drives right now."
    assert "database down" not in " ".join(e.value for e in at.error)  # no raw errors (NFR-SEC-08)
