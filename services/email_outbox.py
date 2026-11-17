"""The demo confirmation email: written as a .eml FILE in outbox/, never sent (US-CHK-04). Owner: User 2.

Rules: build it with email.message.EmailMessage; plain-text and HTML bodies; escape every value in the
HTML (html.escape); safe file name outbox/<order_number>_<cleaned-email>.eml (NFR-SEC-07). No SMTP code.
"""

from __future__ import annotations

from pathlib import Path

from models.order import Order

OUTBOX_DIR = Path("outbox")
FROM_ADDRESS = "orders@keyguard-local.example"


def write_confirmation(order: Order) -> Path:
    """Writes the confirmation email for `order` and returns its path (US-CHK-04, U2-05)."""
    raise NotImplementedError("US-CHK-04: write_confirmation (U2-05)")
