"""U2-05 · US-CHK-04 the .eml in outbox/, and U2-04 · US-CHK-05 the confirmation page."""

from email import message_from_bytes, policy
from email.message import EmailMessage

import pytest
from streamlit.testing.v1 import AppTest

from models.order import Order
from services import email_outbox
from services.orders import get_order, record_email_file
from tests.conftest import APP_FILE, SAMPLE_ORDERS


@pytest.fixture(autouse=True)
def _temp_outbox(tmp_path, monkeypatch):
    """Emails written by these tests go to a throwaway folder, never the real outbox/."""
    monkeypatch.setattr(email_outbox, "OUTBOX_DIR", tmp_path)
    return tmp_path


def _order(**changes) -> Order:
    return Order.from_row({**SAMPLE_ORDERS[0], **changes})


def _body(raw: bytes, kind: str) -> str:
    """The plain-text or HTML part of a saved email, as text."""
    message = message_from_bytes(raw, _class=EmailMessage, policy=policy.default)
    part = message.get_body((kind,))
    assert part is not None, f"the email has no {kind} part"
    return str(part.get_content())


# ---------------------------------------------------------------- the email file (U2-05)


def test_file_name_is_order_number_and_email():
    assert email_outbox.safe_file_name(_order()) == "KG-20261102-0001_customer@example.com.eml"


def test_file_name_can_never_leave_the_outbox():
    name = email_outbox.safe_file_name(_order(customer_email="../../etc/x y@example.com"))
    assert "/" not in name and "\\" not in name and " " not in name
    assert name == "KG-20261102-0001_.._.._etc_x_y@example.com.eml"


def test_email_has_the_right_headers_and_two_bodies(_temp_outbox):
    path = email_outbox.write_confirmation(_order())
    assert path.parent == _temp_outbox and path.is_file()

    raw = path.read_bytes()
    message = message_from_bytes(raw, policy=policy.default)
    assert message["From"] == "orders@keyguard-local.example"
    assert message["To"] == "customer@example.com"
    assert message["Subject"] == "Your KeyGuard Local order KG-20261102-0001"
    for body in (_body(raw, "plain"), _body(raw, "html")):
        assert "KeyGuard Pro 64 GB" in body
        assert "$85.32" in body          # total
        assert "$3.00" in body           # community gift
        assert "not a real order" in body  # demo disclaimer


def test_html_body_escapes_names():
    html = _body(email_outbox.build_message(_order(customer_name="<script>x</script>")).as_bytes(), "html")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_download_works_even_if_the_file_was_deleted():
    # Streamlit Cloud empties outbox/ on restart (NFR-DEP-01): the email is rebuilt instead.
    assert b"KG-20261102-0001" in email_outbox.confirmation_bytes(_order())


# ---------------------------------------------------------------- services/orders.py


def test_get_order_returns_the_order_with_its_lines(fake_client):
    order = get_order("kg-20261102-0001")
    assert order is not None
    assert [line.sku for line in order.lines] == ["KG-PRO-64"]


def test_get_order_unknown_number_is_none(fake_client):
    assert get_order("KG-19990101-0001") is None


def test_record_email_file_sends_only_the_outbox_name(fake_client, _temp_outbox):
    record_email_file("KG-20261102-0001", str(_temp_outbox / "KG-20261102-0001_customer@example.com.eml"))
    assert fake_client.calls[-1] == ("rpc", "set_order_email_file", {
        "p_order_number": "KG-20261102-0001", "p_path": "outbox/KG-20261102-0001_customer@example.com.eml"})


# ---------------------------------------------------------------- the confirmation page (U2-04)


def _open_confirmation(order_number: str) -> AppTest:
    from services.community import community_total_cents

    community_total_cents.clear()
    at = AppTest.from_file(str(APP_FILE), default_timeout=30)
    at.query_params["order"] = order_number
    at.run()
    return at.switch_page("app_pages/checkout.py").run()


def test_confirmation_shows_number_items_gift_and_download(fake_settings, fake_client, as_user):
    as_user("customer")
    at = _open_confirmation("KG-20261102-0001")
    assert not at.exception
    assert at.success[0].value == "Thank you, Demo! Your order KG-20261102-0001 is confirmed."
    assert "You gave **$3.00**" in " ".join(m.value for m in at.markdown)
    assert at.get("download_button")[0].proto.label == "Download confirmation email"


def test_unknown_order_shows_not_found(fake_settings, fake_client, as_user):
    as_user("customer")
    at = _open_confirmation("KG-19990101-0001")
    assert at.warning[0].value == "Order not found."
