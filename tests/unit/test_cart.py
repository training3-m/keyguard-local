"""Tests for the session cart (utils/cart.py): quantity limits and counting (US-CART-01 AC2)."""

import pytest
import streamlit as st

from utils import cart


@pytest.fixture(autouse=True)
def fresh_cart():
    """Each test starts with an empty cart. Outside a running app, st.session_state still works."""
    cart.clear()
    yield
    cart.clear()


def test_add_new_and_existing_sku():
    assert cart.add("KG-PRO-64", 2) == 2
    assert cart.add("KG-PRO-64", 3) == 5
    assert cart.get_cart() == {"KG-PRO-64": 5}


def test_add_never_goes_above_10():
    cart.add("KG-ESS-16", 8)
    assert cart.add("KG-ESS-16", 5) == 10


def test_add_respects_stock_limit():
    assert cart.add("KG-PRO-256", 5, max_qty=3) == 3


def test_update_and_remove():
    cart.add("KG-ACC-LAN", 4)
    assert cart.update("KG-ACC-LAN", 2) == 2
    assert cart.update("KG-ACC-LAN", 0) == 0
    assert "KG-ACC-LAN" not in cart.get_cart()


def test_count_adds_all_quantities():
    cart.add("KG-PRO-64", 2)
    cart.add("KG-ACC-LAN", 1)
    assert cart.count() == 3


def test_clear_empties_the_cart():
    cart.add("KG-PRO-64", 1)
    cart.clear()
    assert cart.count() == 0
    assert st.session_state["cart"] == {}
