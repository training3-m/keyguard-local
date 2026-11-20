"""The demo confirmation email: written as a .eml FILE in outbox/, never sent (US-CHK-04). Owner: User 2.

Rules: build it with email.message.EmailMessage; plain-text and HTML bodies; escape every value in the
HTML (html.escape); safe file name outbox/<order_number>_<cleaned-email>.eml (NFR-SEC-07). No SMTP code.
"""

from __future__ import annotations

import html
import re
from email.message import EmailMessage
from email.utils import formatdate
from pathlib import Path

from models.order import Order
from utils.formatting import money

# The project's outbox/ folder (git-ignored). Absolute, so it works from any working directory.
OUTBOX_DIR = Path(__file__).resolve().parent.parent / "outbox"
FROM_ADDRESS = "orders@keyguard-local.example"
_UNSAFE = re.compile(r"[^A-Za-z0-9._@-]")
_DISCLAIMER = ("KeyGuard Local is a demo store for a class. This is not a real order: nothing was "
               "charged and nothing will be shipped.")


def safe_file_name(order: Order) -> str:
    """outbox file name: <order_number>_<email>.eml with every other character turned into "_".

    No slashes or backslashes can survive, so the name can never point outside outbox/ (NFR-SEC-07).
    """
    return _UNSAFE.sub("_", f"{order.order_number}_{order.customer_email}") + ".eml"


def _shipping(order: Order) -> str:
    return "FREE" if order.shipping_cents == 0 else money(order.shipping_cents)


def _text_body(order: Order) -> str:
    lines = [f"Hi {order.customer_name},", "", f"Thank you for your order {order.order_number}.", ""]
    lines += [f"  {line.qty} x {line.product_name} ({line.sku})  {money(line.line_total_cents)}"
              for line in order.lines]
    lines += [
        "",
        f"Subtotal: {money(order.subtotal_cents)}",
        f"Shipping: {_shipping(order)}",
        f"Tax (8%): {money(order.tax_cents)}",
        f"Total:    {money(order.total_cents)}",
        "",
        f"You gave {money(order.community_gift_cents)} to the Rancho Public Library Digital Safety Fund.",
        "",
        _DISCLAIMER,
    ]
    return "\n".join(lines) + "\n"


def _html_body(order: Order) -> str:
    """The same content as HTML. Every value goes through html.escape, so a name like <b> stays text."""
    e = html.escape
    rows = "".join(
        f"<tr><td>{line.qty} &times; {e(line.product_name)} ({e(line.sku)})</td>"
        f"<td style='text-align:right'>{e(money(line.line_total_cents))}</td></tr>"
        for line in order.lines
    )
    totals = "".join(
        f"<tr><td>{label}</td><td style='text-align:right'>{e(value)}</td></tr>"
        for label, value in (("Subtotal", money(order.subtotal_cents)), ("Shipping", _shipping(order)),
                             ("Tax (8%)", money(order.tax_cents)), ("<b>Total</b>", money(order.total_cents)))
    )
    return (
        "<html><body style='font-family:Arial,sans-serif'>"
        f"<p>Hi {e(order.customer_name)},</p>"
        f"<p>Thank you for your order <b>{e(order.order_number)}</b>.</p>"
        f"<table cellpadding='4'>{rows}{totals}</table>"
        f"<p>You gave <b>{e(money(order.community_gift_cents))}</b> to the Rancho Public Library "
        "Digital Safety Fund.</p>"
        f"<p style='color:#666'><small>{e(_DISCLAIMER)}</small></p>"
        "</body></html>"
    )


def build_message(order: Order) -> EmailMessage:
    """The confirmation email (US-CHK-04 AC2): From, To, Subject, plain-text and HTML bodies."""
    message = EmailMessage()
    message["From"] = FROM_ADDRESS
    message["To"] = order.customer_email
    message["Subject"] = f"Your KeyGuard Local order {order.order_number}"
    message["Date"] = formatdate(localtime=True)
    message.set_content(_text_body(order))
    message.add_alternative(_html_body(order), subtype="html")
    return message


def write_confirmation(order: Order) -> Path:
    """Writes the confirmation email for `order` and returns its path (US-CHK-04, U2-05)."""
    OUTBOX_DIR.mkdir(exist_ok=True)
    path = OUTBOX_DIR / safe_file_name(order)
    path.write_bytes(build_message(order).as_bytes())
    return path


def confirmation_bytes(order: Order) -> bytes:
    """The .eml for the download button: the saved file if it is still there, otherwise rebuilt.

    On Streamlit Community Cloud, outbox/ is emptied when the app restarts (NFR-DEP-01), so the
    download must still work without the file.
    """
    path = OUTBOX_DIR / safe_file_name(order)
    if path.is_file():
        return path.read_bytes()
    return build_message(order).as_bytes()
