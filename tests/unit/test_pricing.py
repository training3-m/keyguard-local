"""Tests for cart totals (utils/pricing.py). Must match place_order() in 0007 and 01-product.md §A6."""

from models.cart import CartLine
from utils.formatting import money
from utils.pricing import calculate_totals, tax_for


def line(price: int, qty: int, gift: int = 0) -> CartLine:
    return CartLine(sku="KG-TEST", name="Test", unit_price_cents=price, qty=qty, community_gift_cents=gift)


def test_scenario_4_free_shipping_tax_and_total():
    # 01-product.md Part C, scenario 4: subtotal $167.00 -> FREE shipping, $13.36 tax, $180.36 total
    totals = calculate_totals([line(7900, 2, gift=300), line(900, 1, gift=50)])
    assert totals.subtotal_cents == 16700
    assert totals.shipping_cents == 0
    assert totals.tax_cents == 1336
    assert totals.total_cents == 18036
    assert totals.community_gift_cents == 650
    assert totals.free_shipping_gap_cents == 0


def test_under_75_pays_shipping_and_shows_gap():
    totals = calculate_totals([line(4900, 1)])
    assert totals.shipping_cents == 499
    assert totals.free_shipping_gap_cents == 7500 - 4900


def test_exactly_75_ships_free():
    assert calculate_totals([line(7500, 1)]).shipping_cents == 0


def test_same_total_as_database_test():
    # tests/place_order_test.sql TEST 3: $10.00 + $4.99 shipping + $0.80 tax = $15.79
    assert calculate_totals([line(1000, 1)]).total_cents == 1579


def test_empty_cart_costs_nothing():
    totals = calculate_totals([])
    assert (totals.subtotal_cents, totals.shipping_cents, totals.total_cents) == (0, 0, 0)


def test_tax_rounds_half_up():
    assert tax_for(1006) == 80   # 80.48 -> 80
    assert tax_for(1019) == 82   # 81.52 -> 82
    assert tax_for(1025) == 82   # 82.00 exactly
    assert tax_for(6) == 0       # 0.48 -> 0
    assert tax_for(19) == 2      # 1.52 -> 2


def test_money_format():
    assert money(18036) == "$180.36"
    assert money(123456) == "$1,234.56"
    assert money(0) == "$0.00"
