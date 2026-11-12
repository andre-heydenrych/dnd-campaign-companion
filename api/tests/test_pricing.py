from decimal import Decimal

from app.shop_service import calculate_price, round_price


def test_price_is_plain_multiplication():
    # 10 x 1.5 x 2 x 0.5 = 15
    assert calculate_price(10, 1.5, 2, 0.5) == Decimal("15.00")


def test_no_modifiers_returns_cost():
    assert calculate_price(15, 1.0, 1.0, 1.0) == Decimal("15.00")


def test_rounds_half_up_where_python_round_would_not():
    # 0.25 x 0.5 = 0.125. Python's round() uses banker's rounding: 0.12.
    assert round(0.125, 2) == 0.12
    assert calculate_price(0.25, 0.5, 1.0, 1.0) == Decimal("0.13")


def test_round_price_handles_floats_that_are_not_exact_in_binary():
    # The float 2.675 is really 2.67499999..., so round() gives 2.67.
    assert round(2.675, 2) == 2.67
    assert round_price(2.675) == Decimal("2.68")


def test_modifiers_below_one_lower_the_price():
    # 75 x 0.9 x 0.8 x 0.95 = 51.3
    assert calculate_price(75, 0.9, 0.8, 0.95) == Decimal("51.30")


def test_modifiers_above_one_raise_the_price():
    # 25 x 1.1 x 1.2 x 1.05 = 34.65
    assert calculate_price(25, 1.1, 1.2, 1.05) == Decimal("34.65")


def test_rounds_only_once_at_the_end():
    # 0.1 x 1.15 x 1.15 x 1.15 = 0.1520875 -> 0.15.
    # Rounding after every step would give 0.12 -> 0.14 -> 0.16 instead.
    assert calculate_price(0.1, 1.15, 1.15, 1.15) == Decimal("0.15")
