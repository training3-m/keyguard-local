"""Cart totals: shipping, tax and the community gift (01-product.md §A6).

Used by US-CART-02 (cart), US-CART-03 (free_shipping_gap_cents for the free-shipping hint) and checkout.

The database recalculates the same totals in place_order() (0007), which is what the order
really uses. This copy only SHOWS the shopper the numbers before they check out, so keep the two
in step: free shipping from $75, otherwise $4.99; 8% tax on the subtotal, rounded half up.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from models.cart import CartLine, Totals

FREE_SHIPPING_FROM_CENTS = 7500
SHIPPING_CENTS = 499
TAX_RATE = Decimal("0.08")


def tax_for(subtotal_cents: int) -> int:
    """8% of the subtotal, rounded to the nearest cent (half up, like Postgres round())."""
    return int((Decimal(subtotal_cents) * TAX_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calculate_totals(lines: list[CartLine]) -> Totals:
    """Adds up the cart. An empty cart costs nothing (no shipping charge)."""
    subtotal = sum(line.line_total_cents for line in lines)
    gift = sum(line.gift_total_cents for line in lines)

    if subtotal == 0:
        shipping = 0
    elif subtotal >= FREE_SHIPPING_FROM_CENTS:
        shipping = 0
    else:
        shipping = SHIPPING_CENTS

    tax = tax_for(subtotal)
    gap = 0 if subtotal == 0 or subtotal >= FREE_SHIPPING_FROM_CENTS else FREE_SHIPPING_FROM_CENTS - subtotal
    return Totals(
        subtotal_cents=subtotal,
        shipping_cents=shipping,
        tax_cents=tax,
        total_cents=subtotal + shipping + tax,
        community_gift_cents=gift,
        free_shipping_gap_cents=gap,
    )
