"""One order's lines and totals: used by My orders (U2-08) and Manage orders (U3-07).

Shared by two users, so a change here needs the Tech Lead AND both users to review (plan §5.5 X2).
"""

from __future__ import annotations

import streamlit as st

from components.badges import community_chip, order_status_badge
from models.order import Order
from utils.formatting import money


def order_detail(order: Order) -> None:
    """Order number, status, date, the lines table and the totals."""
    with st.container(border=True, key=f"order_{order.order_number}"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown(f"**{order.order_number}**")
            order_status_badge(order.status)
        st.caption(f"Placed {order.created_at[:10]} · {order.customer_name}")

        st.table(
            [{"Product": line.product_name, "SKU": line.sku, "Qty": line.qty,
              "Price": money(line.unit_price_cents), "Line total": money(line.line_total_cents)}
             for line in order.lines],
            alt=f"Items in order {order.order_number}",
        )

        st.table(
            {"": ["Subtotal", "Shipping", "Tax", "Total"],
             "Amount": [money(order.subtotal_cents),
                        "FREE" if order.shipping_cents == 0 else money(order.shipping_cents),
                        money(order.tax_cents), money(order.total_cents)]},
            alt=f"Totals for order {order.order_number}",
        )
        community_chip(order.community_gift_cents)
