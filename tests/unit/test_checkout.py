"""U2-03 · US-CHK-02/03 checkout: validation/checkout.py, services/orders.place_order, the page."""

from uuid import uuid4

import pytest
from postgrest.exceptions import APIError
from streamlit.testing.v1 import AppTest

from services.orders import GENERIC_ORDER_ERROR, OrderError, place_order
from tests.conftest import APP_FILE
from validation.checkout import checkout_errors

GOOD_SHIPPING = {"full_name": "Demo Customer", "address": "1 Library Way", "city": "Rancho", "zip": "91730"}
PLACED = {"order_number": "KG-20261119-0001", "order_id": 9, "subtotal_cents": 7900, "shipping_cents": 0,
          "tax_cents": 632, "total_cents": 8532, "community_gift_cents": 300, "already_placed": False}


def _db_error(code: str, message: str) -> APIError:
    return APIError({"code": code, "message": message, "details": None, "hint": None})


# ---------------------------------------------------------------- validation


def test_good_form_has_no_errors():
    assert checkout_errors(GOOD_SHIPPING, demo_confirmed=True) == {}


@pytest.mark.parametrize(
    ("field", "value"),
    [("full_name", "A"), ("address", "   "), ("city", ""), ("zip", "1234"), ("zip", "9173O")],
)
def test_each_bad_field_gets_its_own_message(field, value):
    errors = checkout_errors({**GOOD_SHIPPING, field: value}, demo_confirmed=True)
    assert list(errors) == [field]


def test_demo_box_must_be_ticked():
    assert "demo" in checkout_errors(GOOD_SHIPPING, demo_confirmed=False)


# ---------------------------------------------------------------- service


def test_place_order_sends_only_skus_and_quantities(fake_client):
    fake_client.rpc_results["place_order"] = PLACED
    key = uuid4()
    assert place_order({"KG-PRO-64": 1}, GOOD_SHIPPING, key)["order_number"] == "KG-20261119-0001"
    name, params = fake_client.calls[-1][1:]
    assert name == "place_order"
    assert params == {"p_items": [{"sku": "KG-PRO-64", "qty": 1}], "p_shipping": GOOD_SHIPPING,
                      "p_idempotency_key": str(key)}  # no prices: the database looks them up


def test_out_of_stock_is_a_friendly_error(fake_client):
    fake_client.rpc_results["place_order"] = _db_error("23514", "Not enough stock for KeyGuard Pro 64 GB (only 1 left)")
    with pytest.raises(OrderError) as caught:
        place_order({"KG-PRO-64": 2}, GOOD_SHIPPING, uuid4())
    assert caught.value.out_of_stock
    assert caught.value.message == "Not enough stock for KeyGuard Pro 64 GB (only 1 left)"


def test_unexpected_database_error_hides_the_details(fake_client):
    fake_client.rpc_results["place_order"] = _db_error("XX000", "internal: relation secret_table")
    with pytest.raises(OrderError) as caught:
        place_order({"KG-PRO-64": 1}, GOOD_SHIPPING, uuid4())
    assert caught.value.message == GENERIC_ORDER_ERROR
    assert not caught.value.out_of_stock


# ---------------------------------------------------------------- page


def _open_checkout(items: dict[str, int]) -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    at = AppTest.from_file(str(APP_FILE), default_timeout=30)
    at.session_state["cart"] = dict(items)
    at.run()
    return at.switch_page("app_pages/checkout.py").run()


def _fill(at: AppTest, *, demo: bool = True, zip_code: str = "91730") -> AppTest:
    at.text_input(key="checkout_address").input("1 Library Way")
    at.text_input(key="checkout_city").input("Rancho")
    at.text_input(key="checkout_zip").input(zip_code)
    if demo:
        at.checkbox(key="checkout_demo").check()
    return at


def _submit(at: AppTest) -> AppTest:
    """Clicks Place order (found by its label: the menu has a Sign out button too)."""
    place = next(b for b in at.button if b.label == "Place order")
    return place.click().run()


def test_form_shows_email_readonly_and_prefilled_name(fake_settings, fake_client, as_user):
    as_user("customer")
    at = _open_checkout({"KG-PRO-64": 1})
    assert not at.exception
    email = at.text_input[0]
    assert email.value == "customer@example.com" and email.disabled
    assert at.text_input(key="checkout_full_name").value == "Demo Customer"
    labels = " ".join(t.label.lower() for t in at.text_input)
    assert not any(word in labels for word in ("card", "cvv", "payment"))  # AC2


def test_placing_an_order_clears_the_cart_and_shows_the_number(fake_settings, fake_client, as_user):
    fake_client.rpc_results["place_order"] = PLACED
    as_user("customer")
    at = _submit(_fill(_open_checkout({"KG-PRO-64": 1})))
    assert not at.exception
    assert at.session_state["cart"] == {}
    assert at.query_params["order"] == "KG-20261119-0001"
    assert "KG-20261119-0001" in at.success[0].value
    assert [c for c in fake_client.calls if c[:2] == ("rpc", "place_order")]


def test_bad_zip_is_shown_under_the_field_and_nothing_is_sent(fake_settings, fake_client, as_user):
    as_user("customer")
    at = _submit(_fill(_open_checkout({"KG-PRO-64": 1}), zip_code="12"))
    assert "ZIP code must be exactly 5 digits" in " ".join(e.value for e in at.error)
    assert not [c for c in fake_client.calls if c[:2] == ("rpc", "place_order")]
    assert at.session_state["cart"] == {"KG-PRO-64": 1}


def test_out_of_stock_sends_the_shopper_back_to_the_cart(fake_settings, fake_client, as_user):
    fake_client.rpc_results["place_order"] = _db_error("23514", "Not enough stock for KeyGuard Pro 64 GB (only 0 left)")
    as_user("customer")
    at = _submit(_fill(_open_checkout({"KG-PRO-64": 1})))
    assert "Not enough stock for KeyGuard Pro 64 GB" in " ".join(e.value for e in at.error)
    assert at.session_state["cart"] == {"KG-PRO-64": 1}  # nothing changed (US-CHK-03 AC2)
    assert any(p.proto.label == "Review your cart" for p in at.get("page_link"))


def test_same_key_is_reused_after_a_failed_try(fake_settings, fake_client, as_user):
    fake_client.rpc_results["place_order"] = _db_error("22023", "Please enter your address and city")
    as_user("customer")
    at = _submit(_fill(_open_checkout({"KG-PRO-64": 1})))
    first_key = at.session_state["checkout_key"]
    fake_client.rpc_results["place_order"] = PLACED
    at = _submit(at)
    keys = [c[2]["p_idempotency_key"] for c in fake_client.calls if c[:2] == ("rpc", "place_order")]
    assert keys == [first_key, first_key]  # a retry can never create a second order


def test_empty_cart_shows_empty_state(fake_settings, fake_client, as_user):
    as_user("customer")
    at = _open_checkout({})
    assert "Your cart is empty." in " ".join(m.value for m in at.markdown)
