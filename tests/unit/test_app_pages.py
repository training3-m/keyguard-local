"""Example Streamlit AppTest for PAGES (Prompt F): runs the real app headless, no browser, no database.

`as_user` picks who is signed in; `fake_settings` means no secrets file is needed (works in CI).
Copy this pattern to test your page: switch to it, run, and check what it shows.
"""

from streamlit.testing.v1 import AppTest

from tests.conftest import APP_FILE


def _open(page: str | None = None) -> AppTest:
    at = AppTest.from_file(str(APP_FILE), default_timeout=30).run()
    if page:
        at.switch_page(page).run()
    return at


def _all_text(at: AppTest) -> str:
    parts = [m.value for m in at.markdown] + [i.value for i in at.info] + [e.value for e in at.error]
    return " ".join(str(p) for p in parts)


def test_shop_opens_for_a_guest(fake_settings, as_user):
    as_user(None)
    at = _open()
    assert not at.exception
    assert at.title[0].value == "Shop"


def test_checkout_asks_a_guest_to_sign_in(fake_settings, as_user):
    as_user(None)
    at = _open("app_pages/checkout.py")
    assert not at.exception
    assert "Sign in to check out" in _all_text(at)  # US-CHK-01 gate


def test_checkout_remembers_where_to_return(fake_settings, as_user):
    as_user(None)
    at = _open("app_pages/checkout.py")
    assert at.session_state["return_to"] == "app_pages/checkout.py"  # US-CART-04


def test_staff_can_open_the_dashboard(fake_settings, as_user):
    as_user("staff")
    at = _open("app_pages/manage_dashboard.py")
    assert not at.exception
    text = _all_text(at)
    assert "orders, units sold" in text  # the US-MGT-08 dashboard placeholder
    assert "revenue" not in text  # revenue tiles are owner only (US-MGT-08 AC2)


def test_owner_sees_owner_only_extras(fake_settings, as_user):
    as_user("owner")
    at = _open("app_pages/manage_dashboard.py")
    assert "revenue" in _all_text(at)


def test_customer_signed_in_sees_account_page(fake_settings, as_user):
    as_user("customer")
    at = _open("app_pages/account.py")
    assert not at.exception
    assert len(at.tabs) == 2  # Profile and My orders
