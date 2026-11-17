"""Tests for the register / sign-in form checks (validation/auth.py, NFR-AUTH-02)."""

from validation.auth import email_error, full_name_error, password_checklist, password_error


def test_good_password_has_no_error():
    assert password_error("keyguard123") is None


def test_short_password_is_rejected():
    assert "8+ characters" in password_error("abc12")


def test_password_needs_a_number_and_a_letter():
    assert "a number" in password_error("onlyletters")
    assert "a letter" in password_error("12345678")


def test_password_longer_than_72_is_rejected():
    assert "72" in password_error("a1" * 40)


def test_checklist_reports_each_rule():
    assert password_checklist("abc") == {"8+ characters": False, "A letter": True, "A number": False}


def test_email_check():
    assert email_error("sam@example.com") is None
    assert email_error("not-an-email") is not None
    assert email_error("sam@example") is not None


def test_full_name_length():
    assert full_name_error("Sam") is None
    assert full_name_error("S") is not None
    assert full_name_error("x" * 81) is not None
