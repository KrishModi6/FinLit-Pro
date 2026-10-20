"""Number formatting used in every view, the brief and the report."""

import math

from finlit_pro.fmt import dollars, money, num, pct


def test_no_negative_zero():
    assert num(-0.001) == "0.00" and num(-0.001, sign=True) == "+0.00"
    assert pct(-0.00001, 1, True) == "+0.0%"
    assert money(-0.004) == "$0.00"


def test_missing_values_read_n_a():
    for f in (num, pct, money):
        assert f(None) == "n/a" and f(math.nan) == "n/a" and f(math.inf) == "n/a"


def test_compact_money():
    assert money(1.234e12) == "$1.2T" and money(-21.9e9) == "-$21.9B" and money(12_345) == "$12.3K"


def test_exact_dollars_for_positions():
    assert dollars(1085) == "$1,085.00" and dollars(-90.104, sign=True) == "-$90.10" and dollars(0.001, sign=True) == "+$0.00"
