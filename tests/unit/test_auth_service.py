"""Example unit test for a SERVICE function (Prompt F), using the fake Supabase client from conftest.py.

Copy this pattern for your story: ask for `fake_client`, call the service, check the result and
fake_client.calls. No real database is used.
"""

import pytest

from services import auth
from utils import cart


def test_sign_in_loads_name_and_role(fake_client):
    user = auth.sign_in("owner@example.com", "owner-pass-1")
    assert (user.full_name, user.role) == ("Demo Owner", "owner")
    assert auth.current_user() == user


def test_wrong_password_gives_the_same_message_as_unknown_email(fake_client):
    with pytest.raises(auth.AuthError) as wrong_password:
        auth.sign_in("owner@example.com", "nope-1234")
    with pytest.raises(auth.AuthError) as unknown_email:
        auth.sign_in("nobody@example.com", "nope-1234")
    assert str(wrong_password.value) == str(unknown_email.value) == auth.SIGN_IN_ERROR  # NFR-AUTH-03


def test_five_wrong_passwords_lock_the_form(fake_client):
    for _ in range(auth.MAX_FAILED_SIGN_INS):
        with pytest.raises(auth.AuthError):
            auth.sign_in("customer@example.com", "wrong-pass-1")
    assert auth.lockout_seconds_left() > 0
    with pytest.raises(auth.AuthError, match="Too many"):  # even the right password waits
        auth.sign_in("customer@example.com", "customer-pass-1")


def test_register_always_creates_a_customer(fake_client):
    user = auth.register("Sam Lee", "sam@example.com", "keyguard123")
    assert user.role == "customer"


def test_register_rejects_a_weak_password_before_calling_supabase(fake_client):
    with pytest.raises(auth.AuthError, match="Password needs"):
        auth.register("Sam Lee", "sam@example.com", "short")


def test_sign_out_keeps_the_cart(fake_client):
    auth.sign_in("customer@example.com", "customer-pass-1")
    cart.add("KG-PRO-64", 2)
    auth.sign_out()
    assert auth.current_user() is None
    assert cart.get_cart() == {"KG-PRO-64": 2}  # US-AUTH-03 AC1
